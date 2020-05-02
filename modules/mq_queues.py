# -*- coding: utf-8 -*-
import re
import time
import datetime
from log.logger_client import set_logger
from modules.mq_api import (
    run_mq_command,
    add_annotation)


logger = set_logger()


def get_metric_name(metric_label):
    return 'mq_queue_{0}'.format(metric_label)


def get_metric_annotation():
    annotations = {
        'maxdepth': ['# HELP {0} Maximum depth of queue.\n\
# TYPE {0} gauge\n'.format(get_metric_name('maxdepth')), 0],
        'curdepth': ['# HELP {0} Current depth of queue.\n\
# TYPE {0} gauge\n'.format(get_metric_name('curdepth')), 1]}
    return annotations


def get_metric_annotation_monitor():
    annotations = {
        'msgage': ['# HELP {0} Age of the oldest message on the queue.\n\
# TYPE {0} gauge\n'.format(get_metric_name('msgage')), 0],
        'lput': ['# HELP {0} Timestamp on which the last message was put to the queue.\n\
# TYPE {0} gauge\n'.format(get_metric_name('lput')), 1],
        'lget': ['# HELP {0} Timestamp on which the last message was retrieved from the queue.\n\
# TYPE {0} gauge\n'.format(get_metric_name('lget')), 2],
        'qtime': ['# HELP {0} Interval between messages being put on the queue and then being destructively read.\n\
# TYPE {0} gauge\n'.format(get_metric_name('qtime')), 3]}
    return annotations


def get_queues_metrics(mq_manager):
    queue_labels_data = run_mq_command(task='get_queues', mqm=mq_manager)
    queues_labels = get_queues_labels(queue_labels_data)
    queues_metrics = make_metrics_data_for_queues(queues_labels, mq_manager)
    return queues_metrics


def get_queues_metrics_monitor(mq_manager):
    queue_labels_data_monitor = run_mq_command(task='get_queues_monitor', mqm=mq_manager)
    queues_labels_monitor = get_queues_labels_monitor(queue_labels_data_monitor)
    queues_metrics_monitor = make_metrics_data_for_queues_monitor(queues_labels_monitor, mq_manager)
    return queues_metrics_monitor


def get_queues_labels(queue_labels_data):
    queue_regexp = r'QUEUE\(([^)]+)\)'
    curdepth_regexp = r'CURDEPTH\(([^)]+)\)'
    maxdepth_regexp = r'MAXDEPTH\(([^)]+)\)'
    queue_type_regexp = r'TYPE\(([^)]+)\)'
    queues_labels = {}
    for item in queue_labels_data.split('Display Queue details'):
        if not item:
            continue
        queue = re.search(queue_regexp, item)
        curdepth = re.search(curdepth_regexp, item)
        maxdepth = re.search(maxdepth_regexp, item)
        queue_type = re.search(queue_type_regexp, item)
        if all(label is not None for label in [queue, curdepth, maxdepth, queue_type]):
            queues_labels[queue.group(1)] = {
                'curdepth': curdepth.group(1),
                'maxdepth': maxdepth.group(1),
                'type': queue_type.group(1)}
    return queues_labels


def make_metrics_data_for_queues(queues_labels, mq_manager):
    metrics_annotation = get_metric_annotation()
    prometheus_data_list = list(list() for i in range(len(metrics_annotation)))
    prometheus_data_list_result = list()
    for queue_name, queue_labels in queues_labels.items():
        template_string = 'qmname="{0}", queuename="{1}", type="{2}"'.format(
            mq_manager,
            queue_name,
            queue_labels['type'])
        max_depth_metric = '{0}{{{1}}} {2}\n'.format(
            get_metric_name('maxdepth'),
            template_string,
            int(queue_labels['maxdepth']))
        cur_depth_metric = '{0}{{{1}}} {2}\n'.format(
            get_metric_name('curdepth'),
            template_string,
            int(queue_labels['curdepth']))
        prometheus_data_list[metrics_annotation['maxdepth'][1]].append(max_depth_metric)
        prometheus_data_list[metrics_annotation['curdepth'][1]].append(cur_depth_metric)
    for key in sorted(metrics_annotation.keys()):
        add_annotation(prometheus_data_list[metrics_annotation[key][1]], metrics_annotation[key][0])
        prometheus_data_list_result.extend(prometheus_data_list[metrics_annotation[key][1]])
    prometheus_data_str = ''.join(prometheus_data_list_result)
    return prometheus_data_str


def get_queues_labels_monitor(queue_labels_data):
    queue_regexp = r'QUEUE\(([^)]+)\)'
    lgettime_regexp = r'LGETTIME\(([^)]+)\)'
    lputtime_regexp = r'LPUTTIME\(([^)]+)\)'
    lgetdate_regexp = r'LGETDATE\(([^)]+)\)'
    lputdate_regexp = r'LPUTDATE\(([^)]+)\)'
    msgage_regexp = r'MSGAGE\(([^)]+)\)'
    qtime_regexp = r'QTIME\(([^)]+)\)'
    monq_regexp = r'MONQ\(([^)]+)\)'
    queues_labels_monitor = {}
    for item in queue_labels_data.split('Display queue status details'):
        if not item:
            continue
        monq = re.search(monq_regexp, item)
        lgettime = re.search(lgettime_regexp, item)
        lputtime = re.search(lputtime_regexp, item)
        lgetdate = re.search(lgetdate_regexp, item)
        lputdate = re.search(lputdate_regexp, item)
        queue = re.search(queue_regexp, item)
        msgage = re.search(msgage_regexp, item)
        qtime = re.search(qtime_regexp, item)
        if all(label is not None for label in [queue, lgettime, lputtime, lgetdate, lputdate, msgage, qtime]):
            if any([monq.group(1) == "OFF", not lgettime.group(1).strip(),
                    not lputtime.group(1).strip(), not lputdate.group(1).strip(),
                    not lgetdate.group(1).strip()]):
                continue
            queues_labels_monitor[queue.group(1)] = {
                'lgettime': lgettime.group(1),
                'lputtime': lputtime.group(1),
                'lgetdate': lgetdate.group(1),
                'lputdate': lputdate.group(1),
                'msgage': msgage.group(1),
                'qtime': qtime.group(1)}
    return queues_labels_monitor


def make_metrics_data_for_queues_monitor(queues_labels, mq_manager):
    metrics_annotation = get_metric_annotation_monitor()
    prometheus_data_list = list(list() for i in range(len(metrics_annotation)))
    prometheus_data_list_result = list()
    for queue_name, queue_labels in queues_labels.items():
        value_lput = ' '.join([queue_labels['lputdate'], queue_labels['lputtime']])
        metric_value_lput = time.mktime(datetime.datetime.strptime(value_lput, "%Y-%m-%d %H.%M.%S").timetuple())
        value_lget = ' '.join([queue_labels['lgetdate'], queue_labels['lgettime']])
        metric_value_lget = time.mktime(datetime.datetime.strptime(value_lget, "%Y-%m-%d %H.%M.%S").timetuple())
        template_string = 'qmname="{0}", queuename="{1}"'.format(
            mq_manager,
            queue_name)
        msgage_metric = '{0}{{{1}}} {2}\n'.format(
            get_metric_name('msgage'),
            template_string,
            int(queue_labels['msgage']))
        lput_metric = '{0}{{{1}}} {2}\n'.format(
            get_metric_name('lput'),
            template_string,
            int(metric_value_lput))
        lget_metric = '{0}{{{1}}} {2}\n'.format(
            get_metric_name('lget'),
            template_string,
            int(metric_value_lget))
        metric_name_qtime_short = '{0}{{{1}, indicator="short_term"}} {2}\n'.format(
            get_metric_name('qtime'),
            template_string,
            int(queue_labels['qtime'].split(',')[0]))
        metric_name_qtime_long = '{0}{{{1}, indicator="long_term"}} {2}\n'.format(
            get_metric_name('qtime'),
            template_string,
            int(queue_labels['qtime'].split(',')[1].strip()))
        prometheus_data_list[metrics_annotation['msgage'][1]].append(msgage_metric)
        prometheus_data_list[metrics_annotation['lput'][1]].append(lput_metric)
        prometheus_data_list[metrics_annotation['lget'][1]].append(lget_metric)
        prometheus_data_list[metrics_annotation['qtime'][1]].extend([
            metric_name_qtime_short,
            metric_name_qtime_long])
    for key in sorted(metrics_annotation.keys()):
        add_annotation(prometheus_data_list[metrics_annotation[key][1]], metrics_annotation[key][0])
        prometheus_data_list_result.extend(prometheus_data_list[metrics_annotation[key][1]])
    prometheus_data_str = ''.join(prometheus_data_list_result)
    return prometheus_data_str
