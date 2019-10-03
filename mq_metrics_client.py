#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import traceback
import platform
import requests
from modules.mq_manager import (
     get_mq_manager_status,
     get_mq_managers,
     make_metric_for_mq_manager_status
     )
from modules.mq_listener import (
     get_listeners,
     get_listener_status,
     make_metric_for_mq_listener_status
     )
from modules.mq_queues import get_queues_labels, make_metrics_data_for_queues
from modules.mq_channels import (
     get_channel_status,
     make_metric_for_mq_channels_status,
     get_channels,
     extract_channel_name,
     format_channel_output
     )
from log.logger_client import set_logger
from requests import ConnectionError
from urllib3.exceptions import ResponseError
import time
from modules.mq_api import run_mq_command


logger = set_logger()


class PrometheusBadResponse(Exception):
    pass


def put_metric_to_gateway(metric_data, job):
    hostname = platform.node()
    port = 9091
    src_url = "http://{0}:{1}".format(hostname, port)
    headers = {"Content-Type": "text/plain; version=0.0.4"}
    dest_url = "{0}/metrics/job/{1}".format(src_url, job)
    logger.info("Destination url: {0}".format(dest_url))
    try:
        response = requests.put(dest_url, data=metric_data, headers=headers)
        if not response.ok:
            raise PrometheusBadResponse("Bad response - {0} from {1}\nResponseText: {2}".format(response, dest_url, response.text))
        logger.info("Success! Server response: {0}".format(response))
    except (ConnectionError, ResponseError):
        raise PrometheusBadResponse("{0} is not available!".format(dest_url))


def get_mq_manager_metrics(mq_manager):
    mq_manager_data = run_mq_command(task='get_mq_manager_status', mqm=mq_manager)
    mqm_status_data = get_mq_manager_status(mq_manager_data)
    metric_data, status = make_metric_for_mq_manager_status(mqm_status_data)
    if status != 1:
        logger.warning("The status of mq_manager - {0} is {1} !\n \
                        Other metrics will not be collected!".format(
                            mq_manager,
                            status
                            ))
    return metric_data, status


def get_mq_listeners_metrics(listeners, mq_manager):
    prometheus_data_list = []
    for listener in listeners:
        listener_data = run_mq_command(
            task='get_lsstatus',
            mqm=mq_manager,
            listener=listener
            )
        listener_labels = run_mq_command(
            task='get_listener',
            mqm=mq_manager,
            listener=listener
            )
        listener_status = get_listener_status(
            listener_name=listener,
            mqm=mq_manager,
            listener_data=listener_data,
            listener_labels=listener_labels
            )
        metric_data = make_metric_for_mq_listener_status(
            listener,
            listener_status,
            mq_manager
            )
        prometheus_data_list.append("{0}".format(metric_data))
    prometheus_data_str = ''.join(prometheus_data_list)
    return prometheus_data_str


def get_mq_channels_metrics(mq_channels, mq_manager):
    prometheus_data_list = []
    for channels in mq_channels:
        for channel in channels:
            channel_data, conn_count = channel
            metric_data_conn = make_metric_for_mq_channels_status(
                channel_data,
                mq_manager,
                'connection_count',
                conn_count
                )
            metric_data_stat = make_metric_for_mq_channels_status(
                channel_data,
                mq_manager,
                'status'
                )
            prometheus_data_list.append("{0}{1}".format(metric_data_conn, metric_data_stat))
    prometheus_data_str = ''.join(prometheus_data_list)
    return prometheus_data_str


def get_queues_metrics(mq_manager):
    queue_labels_data = run_mq_command(task='get_queues', mqm=mq_manager)
    queues_labels = get_queues_labels(queue_labels_data)
    queues_metrics = make_metrics_data_for_queues(queues_labels, mq_manager)
    return queues_metrics


def channels_status(mqm):
    channels = run_mq_command(task='get_channels', mqm=mqm)
    channels_list = get_channels(channels)
    mq_channels_status = {}
    for channel in channels_list:
        channel_name = extract_channel_name(channel)
        if channel_name:
            channel_data = run_mq_command(
                task='get_chstatus',
                mqm=mqm,
                channel=channel_name
                )
            labels_data = []
            stop_flag = "not found"
            if stop_flag in channel_data:
                channel_labels = run_mq_command(
                    task='get_channel',
                    mqm=mqm,
                    channel=channel_name
                    )
                labels_data = format_channel_output(channel_labels)
            else:
                labels_data = format_channel_output(channel_data)
            channel_status = get_channel_status(channel_data, labels_data)
            mq_channels_status[channel_name] = channel_status
    result = []
    for channel_name, channel_labels in mq_channels_status.items():
        middle_result = []
        for channel in channel_labels:
            count = channel_labels.count(channel)
            if (channel, count) not in middle_result:
                middle_result.append((channel, count))
        result.append(middle_result)
    return result


def main():
    start_time = time.time()
    try:
        mq_managers_data = run_mq_command(task='get_mq_managers')
        mq_managers = get_mq_managers(mq_managers_data)
        for mq_manager in mq_managers:
            mq_manager_metrics, status = get_mq_manager_metrics(mq_manager)
            if status == 1:
                listeners_data = run_mq_command(task='get_listeners', mqm=mq_manager)
                listeners = get_listeners(listeners_data)
                mq_listeners_metrics = get_mq_listeners_metrics(listeners, mq_manager)
                mq_channels = channels_status(mq_manager)
                mq_channels_metrics = get_mq_channels_metrics(mq_channels, mq_manager)
                mq_queues_metrics = get_queues_metrics(mq_manager)
                metric_data = "{0}{1}{2}{3}".format(
                    mq_manager_metrics,
                    mq_listeners_metrics,
                    mq_channels_metrics,
                    mq_queues_metrics
                    )
                put_metric_to_gateway(metric_data, mq_manager)
                logger.info("All metrics pushed successfully!")
            else:
                put_metric_to_gateway(mq_manager_metrics, mq_manager)
                logger.warning("Pushed only metric for mq_manager!")
    except PrometheusBadResponse as error:
        logger.error(error)
    except Exception, e:
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)[0]
        logger.error("Function: {0}\n{1}".format(stk, e))
    logger.info("Script finished in - %s seconds -" % (time.time() - start_time))


if __name__ == "__main__":
    while True:
        main()
        time.sleep(15)
