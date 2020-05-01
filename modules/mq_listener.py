# -*- coding: utf-8 -*-
import re
from log.logger_client import set_logger
from modules.mq_api import (
    run_mq_command,
    add_annotation)


logger = set_logger()


def get_metric_name(metric_label):
    return 'mq_listener_{0}'.format(metric_label)


def get_metric_annotation():
    annotations = {
        'status': '# HELP {0} Current status of MQ listener.\n\
# TYPE {0} gauge\n'.format(get_metric_name('status'))}
    return annotations


def get_mq_listeners_metrics(listeners, mq_manager):
    metrics_annotation = get_metric_annotation()
    prometheus_data_list = list()
    for listener in listeners:
        listener_data = run_mq_command(
            task='get_lsstatus',
            mqm=mq_manager,
            listener=listener)
        listener_labels = run_mq_command(
            task='get_listener',
            mqm=mq_manager,
            listener=listener)
        listener_status = get_listener_status(
            listener_name=listener,
            mqm=mq_manager,
            listener_data=listener_data,
            listener_labels=listener_labels)
        metric_data = make_metric_for_mq_listener_status(
            listener,
            listener_status,
            mq_manager)
        prometheus_data_list.append('{0}'.format(metric_data))
    add_annotation(prometheus_data_list, metrics_annotation['status'])
    prometheus_data_str = ''.join(prometheus_data_list)
    return prometheus_data_str


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
        listener_labels=None):
    status_dict = {
        'STOPPED': 0,
        'STOPING': 1,
        'STARTING': 2,
        'RUNNING': 3}
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
    template_string = 'qmname="{0}", listener="{1}", pid="{2}", ipadd="{3}", port="{4}", trptype="{5}", \
control="{6}", backlog="{7}", startda="{8}", startti="{9}", desc="{10}"'.format(
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
        mq_listener_status_data["DESCR"])
    metric_data = '{0}{{{1}}} {2}\n'.format(
        get_metric_name('status'),
        template_string,
        mq_listener_status_data["STATUS"])
    return metric_data
