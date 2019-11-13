# -*- coding: utf-8 -*-
import re
from log.logger_client import set_logger


logger = set_logger()


def get_queues_labels(queue_labels_data):
    queue_regexp = r'QUEUE\\(([^)]+)\\)'
    curdepth_regexp = r'CURDEPTH\\(([^)]+)\\)'
    maxdepth_regexp = r'MAXDEPTH\\(([^)]+)\\)'
    queue_type_regexp = r'TYPE\\(([^)]+)\\)'
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
                'type': queue_type.group(1)
                }
    return queues_labels


def make_metrics_data_for_queues(queues_labels, mq_manager):
    prometheus_data_list = []
    for queue_name, queue_labels in queues_labels.items():
        metric_name_max_depth = 'mq_queue_{0}'.format('maxdepth')
        metric_name_cur_depth = 'mq_queue_{0}'.format('curdepth')
        max_depth_metric = '%s{qmname="%s", queuename="%s", type="%s"} %d\n' % (
            metric_name_max_depth,
            mq_manager,
            queue_name,
            queue_labels['type'],
            int(queue_labels['maxdepth'])
            )
        cur_depth_metric = '%s{qmname="%s", queuename="%s", type="%s"} %d\n' % (
            metric_name_cur_depth,
            mq_manager,
            queue_name,
            queue_labels['type'],
            int(queue_labels['curdepth'])
            )
        prometheus_data_list.extend([max_depth_metric, cur_depth_metric])
    prometheus_data_str = ''.join(prometheus_data_list)
    return prometheus_data_str
