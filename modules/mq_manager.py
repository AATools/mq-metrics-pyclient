# -*- coding: utf-8 -*-
import re
from log.logger_client import set_logger
from modules.mq_api import run_mq_command


logger = set_logger()


def get_metric_name(metric_label):
    return 'mq_manager_{0}'.format(metric_label)


def get_metric_annotation():
    annotations = {
        'status': '# HELP {0} Current status of MQ manager.\n\
# TYPE {0} gauge\n'.format(get_metric_name('status'))}
    return annotations


def get_mq_manager_metrics(mq_manager):
    metrics_annotation = get_metric_annotation()
    mq_manager_data = run_mq_command(task='get_mq_manager_status', mqm=mq_manager)
    mqm_status_data = get_mq_manager_status(mq_manager_data)
    metric_data, status = make_metric_for_mq_manager_status(mqm_status_data)
    metric_data = '{0}{1}'.format(
        metrics_annotation['status'],
        metric_data)
    if status != 1:
        logger.warning("The status of MQ Manager - {0} is {1} !\n \
                        Other metrics will not be collected!".format(mq_manager, status))
    return metric_data, status


def format_output(data_to_format):
    list_without_brackets = list(filter(
        None,
        [value.strip().replace('(', ' ').replace(')', '') for value in data_to_format]))
    result_dict = {}
    for values in list_without_brackets:
        name = values.split()[0]
        value = ' '.join(values.split()[1:])
        result_dict[name] = value
    if result_dict["STATUS"] == "Running":
        result_dict["STATUS"] = 1
    else:
        result_dict["STATUS"] = 0
    return result_dict


def get_mq_manager_status(mq_manager_data):
    result = format_output(mq_manager_data.split(')'))
    return result


def get_mq_managers(mq_managers_data):
    mq_managers = []
    mqmanager_name_regexp = r'QMNAME\(([^)]+)\)'
    output_list = list(filter(None, mq_managers_data.split('\n')))
    for mq_manager in output_list:
        mq_manager_name = re.search(mqmanager_name_regexp, mq_manager).group(1)
        mq_managers.append(mq_manager_name)
    return mq_managers


def make_metric_for_mq_manager_status(mq_manager_status_data):
    template_string = 'default="{0}", instname="{1}", instpath="{2}", instver="{3}", \
qmname="{4}", standby="{5}"'.format(
        mq_manager_status_data["DEFAULT"],
        mq_manager_status_data["INSTNAME"],
        mq_manager_status_data["INSTPATH"],
        mq_manager_status_data["INSTVER"],
        mq_manager_status_data["QMNAME"],
        mq_manager_status_data["STANDBY"])
    metric_data = '{0}{{{1}}} {2}\n'.format(
        get_metric_name('status'),
        template_string,
        mq_manager_status_data["STATUS"])
    return metric_data, mq_manager_status_data["STATUS"]
