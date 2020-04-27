# -*- coding: utf-8 -*-
import re
import time
import datetime
from log.logger_client import set_logger


logger = set_logger()


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
    prometheus_data_list = []
    for queue_name, queue_labels in queues_labels.items():
        metric_name_max_depth = 'mq_queue_{0}'.format('maxdepth')
        metric_name_cur_depth = 'mq_queue_{0}'.format('curdepth')
        max_depth_metric = '{0}\n{1}\n{2}{{qmname="{3}", queuename="{4}", type="{5}"}} {6}\n'.format(
            '# HELP {0} Maximum depth of queue.'.format(metric_name_max_depth),
            '# TYPE {0} gauge'.format(metric_name_max_depth),
            metric_name_max_depth,
            mq_manager,
            queue_name,
            queue_labels['type'],
            int(queue_labels['maxdepth']))
        cur_depth_metric = '{0}\n{1}\n{2}{{qmname="{3}", queuename="{4}", type="{5}"}} {6}\n'.format(
            '# HELP {0} Current depth of queue.'.format(metric_name_cur_depth),
            '# TYPE {0} gauge'.format(metric_name_cur_depth),
            metric_name_cur_depth,
            mq_manager,
            queue_name,
            queue_labels['type'],
            int(queue_labels['curdepth']))
        prometheus_data_list.extend([max_depth_metric, cur_depth_metric])
    prometheus_data_str = ''.join(prometheus_data_list)
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
    prometheus_data_list = []
    for queue_name, queue_labels in queues_labels.items():
        metric_name_msgage = 'mq_queue_{0}'.format('msgage')
        metric_name_lput = 'mq_queue_{0}'.format('lput')
        metric_name_lget = 'mq_queue_{0}'.format('lget')
        metric_name_qtime = 'mq_queue_{0}'.format('qtime')
        value_lput = ' '.join([queue_labels['lputdate'], queue_labels['lputtime']])
        metric_value_lput = time.mktime(datetime.datetime.strptime(value_lput, "%Y-%m-%d %H.%M.%S").timetuple())
        value_lget = ' '.join([queue_labels['lgetdate'], queue_labels['lgettime']])
        metric_value_lget = time.mktime(datetime.datetime.strptime(value_lget, "%Y-%m-%d %H.%M.%S").timetuple())
        msgage_metric = '{0}\n{1}\n{2}{{qmname="{3}", queuename="{4}"}} {5}\n'.format(
            '# HELP {0} Age of the oldest message on the queue.'.format(metric_name_msgage),
            '# TYPE {0} gauge'.format(metric_name_msgage),
            metric_name_msgage,
            mq_manager,
            queue_name,
            int(queue_labels['msgage']))
        lput_metric = '{0}\n{1}\n{2}{{qmname="{3}", queuename="{4}"}} {5}\n'.format(
            '# HELP {0} Timestamp on which the last message was put to the queue.'.format(metric_name_lput),
            '# TYPE {0} gauge'.format(metric_name_lput),
            metric_name_lput,
            mq_manager,
            queue_name,
            int(metric_value_lput))
        lget_metric = '{0}\n{1}\n{2}{{qmname="{3}", queuename="{4}"}} {5}\n'.format(
            '# HELP {0} Timestamp on which the last message was retrieved from the queue.'.format(metric_name_lget),
            '# TYPE {0} gauge'.format(metric_name_lget),
            metric_name_lget,
            mq_manager,
            queue_name,
            int(metric_value_lget))
        metric_name_qtime_short = '{0}\n{1}\n{2}{{qmname="{3}", queuename="{4}", indicator="short_term"}} {5}\n'.format(
            '# HELP {0} Interval between messages being put on the queue and then being destructively read.'.format(metric_name_qtime),
            '# TYPE {0} gauge'.format(metric_name_qtime),
            metric_name_qtime,
            mq_manager,
            queue_name,
            int(queue_labels['qtime'].split(',')[0]))
        metric_name_qtime_long = '{0}\n{1}\n{2}{{qmname="{3}", queuename="{4}", indicator="long_term"}} {5}\n'.format(
            '# HELP {0} Interval between messages being put on the queue and then being destructively read.'.format(metric_name_qtime),
            '# TYPE {0} gauge'.format(metric_name_qtime),
            metric_name_qtime,
            mq_manager,
            queue_name,
            int(queue_labels['qtime'].split(',')[1].strip()))
        prometheus_data_list.extend([msgage_metric, lput_metric, lget_metric, metric_name_qtime_short, metric_name_qtime_long])
    prometheus_data_str = ''.join(prometheus_data_list)
    return prometheus_data_str
