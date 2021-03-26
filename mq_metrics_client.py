# -*- coding: utf-8 -*-
"""Python client for collecting IBM MQ metrics and exporting to Prometheus pushgateway."""
import sys
import time
import traceback
import platform
import requests
import argparse
from requests import ConnectionError
from urllib3.exceptions import ResponseError
from modules.mq_manager import (
    get_mq_managers,
    get_mq_manager_metrics)
from modules.mq_listener import (
    get_listeners,
    get_mq_listeners_metrics)
from modules.mq_channels import (
    channels_status,
    get_mq_channels_metrics)
from modules.mq_queues import (
    get_queues_metrics,
    get_queues_metrics_monitor)
from log.logger_client import set_logger
from modules.mq_api import run_mq_command


logger = set_logger()


class PrometheusBadResponse(Exception):
    pass


def static_content():
    """Client name and version."""
    name = "mq-metrics-pyclient"
    version = "0.6"
    return '{0} v.{1}'.format(name, version)


def parse_commandline_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(prog='mq_metrics_client.py')
    parser.add_argument('--pghost', metavar='pushgatewayHost', nargs='?', default=platform.node(), dest='pushgateway_host', help='pushgateway host')
    parser.add_argument('--pgport', metavar='pushgatewayPort', nargs='?', default='9091', dest='pushgateway_port', help='pushgateway port')
    parser.add_argument('--collectint', metavar='collectInterval', nargs='?', default=15, type=int, dest='sleep_interval', help='time interval between collecting metrics')
    parser.add_argument('--ssh_connect_string', metavar='ssh_connect_string', nargs='?', dest='ssh_connect_string', default=None, help='user@host to connect to with ssh')
    parser.add_argument('--compatible', metavar='compatible', nargs='?', dest='compatible', default=None, choices=['v7.0', None], help='v7.0 for MQv7.0')
    args = parser.parse_args()
    return args.pushgateway_host, args.pushgateway_port, abs(args.sleep_interval), args.ssh_connect_string, args.compatible


def put_metric_to_gateway(metric_data, job, pushgateway_host, pushgateway_port):
    """Sends data to Prometheus pushgateway."""
    src_url = "http://{0}:{1}".format(pushgateway_host, pushgateway_port)
    headers = {"Content-Type": "text/plain; version=0.0.4"}
    dest_url = "{0}/metrics/job/{1}".format(src_url, job)
    logger.info("Destination url: {0}".format(dest_url))
    # Debug info
    # logger.info("Metric data to push: {0}".format(metric_data))
    try:
        response = requests.put(dest_url, data=metric_data, headers=headers)
        if not response.ok:
            raise PrometheusBadResponse("Bad response - {0} from {1}\nResponseText: {2}".format(response, dest_url, response.text))
        logger.info("Success! Server response: {0}".format(response))
    except (ConnectionError, ResponseError):
        raise PrometheusBadResponse("{0} is not available!".format(dest_url))


def get_mq_metrics(pushgateway_host, pushgateway_port, ssh_connect_string=None, compatible=None):
    start_time = time.time()
    logger.info("Starting metrics collecting for IBM MQ!")
    try:
        mq_managers_data = run_mq_command(task='get_mq_managers', ssh_connect_string=ssh_connect_string)
        mq_managers = get_mq_managers(mq_managers_data=mq_managers_data)
        for mq_manager in mq_managers:
            mq_manager_metrics, status = get_mq_manager_metrics(mq_manager=mq_manager, ssh_connect_string=ssh_connect_string, compatible=compatible)
            if status == 1:
                listeners_data = run_mq_command(task='get_listeners', mqm=mq_manager, ssh_connect_string=ssh_connect_string)
                listeners = get_listeners(listeners_data=listeners_data)
                mq_listeners_metrics = get_mq_listeners_metrics(listeners=listeners, mq_manager=mq_manager, ssh_connect_string=ssh_connect_string)
                mq_channels = channels_status(mqm=mq_manager, ssh_connect_string=ssh_connect_string)
                mq_channels_metrics = get_mq_channels_metrics(mq_channels=mq_channels, mq_manager=mq_manager)
                mq_queues_metrics = get_queues_metrics(mq_manager=mq_manager, ssh_connect_string=ssh_connect_string)
                mq_queues_metrics_monitor = get_queues_metrics_monitor(mq_manager=mq_manager, ssh_connect_string=ssh_connect_string)
                metric_data = '{0}{1}{2}{3}{4}'.format(
                    mq_manager_metrics,
                    mq_listeners_metrics,
                    mq_channels_metrics,
                    mq_queues_metrics,
                    mq_queues_metrics_monitor)
                put_metric_to_gateway(
                    metric_data=metric_data,
                    job=mq_manager,
                    pushgateway_host=pushgateway_host,
                    pushgateway_port=pushgateway_port)
                logger.info("All metrics pushed successfully!")
            else:
                put_metric_to_gateway(
                    metric_data=mq_manager_metrics,
                    job=mq_manager,
                    pushgateway_host=pushgateway_host,
                    pushgateway_port=pushgateway_port)
                logger.warning("Pushed only metric for mq_manager!")
        logger.info("Script finished in - {0} seconds -".format(time.time() - start_time))
    except PrometheusBadResponse as error:
        logger.error(error)
    except Exception as err:
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)[0]
        logger.error("Function: {0}\n{1}".format(stk, err))


if __name__ == "__main__":
    logger.info("Run {0}".format(static_content()))
    pushgateway_host, pushgateway_port, sleep_interval, ssh_connect_string, compatible = parse_commandline_args()
    logger.info("Metrics will be collected every {0} seconds".format(sleep_interval))
    while True:
        get_mq_metrics(
            pushgateway_host=pushgateway_host,
            pushgateway_port=pushgateway_port,
            ssh_connect_string=ssh_connect_string,
            compatible=compatible)
        time.sleep(sleep_interval)
