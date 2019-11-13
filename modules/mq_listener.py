# -*- coding: utf-8 -*-
import re
from log.logger_client import set_logger


logger = set_logger()


def get_listeners(listeners_data):
    default_listener = r'SYSTEM.DEFAULT.LISTENER.TCP'
    listener_str_regexp = r'LISTENER\(([^)]+)\)'
    listeners = re.findall(listener_str_regexp, listeners_data)
    # Remove default listener.
    # Comment line below if you use default listener!
    listeners.remove(default_listener)
    return listeners


def get_listener_labels(labels):
    labels_data = format_output(labels, 'labels')
    return labels_data


def format_output(data_to_format, method):
    # Convert string to list,
    # remove empty list elements and slice status data(elements 4-10),
    # or labels data(elements 4-9), depending on function input
    slice_methods = {'labels': slice(4, 9), 'status': slice(4, 10)}
    format_list = list(filter(None, data_to_format.split('\n')))[slice_methods[method]]
    # Remove reduntant whitespaces from every list element and
    # create nested lists, where separator > 2 whitespaces(use regexp)
    nested_list = [re.split(r'\s{2,}', element.strip()) for element in format_list]
    # Collecting into one list
    flat_list = [item for sublist in nested_list for item in sublist]
    value_regex = r'\(([^}]+)\)'
    key_regex = r'.+?(?=\()'
    value_list = [re.search(value_regex, item).group(1) for item in flat_list]
    key_list = [re.search(key_regex, item).group() for item in flat_list]
    # Return standart dict - key:value
    result = dict(zip(key_list, value_list))
    return result


def get_listener_status(
        listener_name=None,
        mqm=None,
        listener_data=None,
        listener_labels=None
        ):
    status_dict = {
        'STOPPED': 0,
        'STOPING': 1,
        'STARTING': 2,
        'RUNNING': 3,
        }
    stop_flag = "not found"
    if stop_flag in listener_data:
        labels_data = get_listener_labels(listener_labels)
        labels_data['PID'] = ""
        labels_data['STARTTI'] = ""
        labels_data['STARTDA'] = ""
        labels_data['STATUS'] = status_dict['STOPPED']
        return labels_data
    status_data = format_output(listener_data, 'status')
    status_data['STATUS'] = status_dict[status_data['STATUS']]
    return status_data


def make_metric_for_mq_listener_status(listener_name, mq_listener_status_data, mqm):
    metric_name = 'mq_listener_status'
    # Unpack tags
    metric_data = '%s{qmname="%s", listener="%s", pid="%s", ipadd="%s", port="%s", trptype="%s", control="%s", backlog="%s", startda="%s", startti="%s", desc="%s"} %d\n' % (
            metric_name,
            mqm,
            mq_listener_status_data["LISTENER"],
            mq_listener_status_data["PID"],
            mq_listener_status_data["IPADDR"],
            mq_listener_status_data["PORT"],
            mq_listener_status_data["TRPTYPE"],
            mq_listener_status_data["CONTROL"],
            mq_listener_status_data["BACKLOG"],
            mq_listener_status_data["STARTDA"],
            mq_listener_status_data["STARTTI"],
            mq_listener_status_data["DESCR"],
            mq_listener_status_data["STATUS"],
            )
    return metric_data
