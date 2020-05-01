# -*- coding: utf-8 -*-
import sys
import time
import traceback
import platform
import requests
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


def put_metric_to_gateway(metric_data, job):
    hostname = platform.node()
    port = 9091
    src_url = "http://{0}:{1}".format(hostname, port)
    headers = {"Content-Type": "text/plain; version=0.0.4"}
    dest_url = "{0}/metrics/job/{1}".format(src_url, job)
    logger.info("Destination url: {0}".format(dest_url))
    # logger.info("Metric data to push: {0}".format(metric_data))
    try:
        response = requests.put(dest_url, data=metric_data, headers=headers)
        if not response.ok:
            raise PrometheusBadResponse("Bad response - {0} from {1}\nResponseText: {2}".format(response, dest_url, response.text))
        logger.info("Success! Server response: {0}".format(response))
    except (ConnectionError, ResponseError):
        raise PrometheusBadResponse("{0} is not available!".format(dest_url))


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
                mq_queues_metrics_monitor = get_queues_metrics_monitor(mq_manager)
                metric_data = '{0}{1}{2}{3}{4}'.format(
                    mq_manager_metrics,
                    mq_listeners_metrics,
                    mq_channels_metrics,
                    mq_queues_metrics,
                    mq_queues_metrics_monitor)
                put_metric_to_gateway(metric_data, mq_manager)
                logger.info("All metrics pushed successfully!")
            else:
                put_metric_to_gateway(mq_manager_metrics, mq_manager)
                logger.warning("Pushed only metric for mq_manager!")
    except PrometheusBadResponse as error:
        logger.error(error)
    except Exception as err:
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)[0]
        logger.error("Function: {0}\n{1}".format(stk, err))
    logger.info("Script finished in - {0} seconds -".format(time.time() - start_time))


if __name__ == "__main__":
    name = "mq-metrics-pyclient"
    version = "0.4"
    logger.info("Run {0} v.{1}".format(name, version))
    while True:
        main()
        time.sleep(15)
