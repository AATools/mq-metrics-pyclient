# -*- coding: utf-8 -*-
"""Tests for `mq_queues`."""
import os
import sys
import unittest
import time
import datetime
from modules.mq_queues import (
    make_metrics_data_for_queues,
    get_queues_labels,
    make_metrics_data_for_queues_monitor,
    get_queues_labels_monitor,
    get_metric_name,
    get_metric_annotation,
    get_metric_annotation_monitor)
sys.path.append(os.getcwd())


class TestGetQueuesLabels(unittest.TestCase):
    def test_get_queues_labels(self):
        """Test for `get_queues_labels` function."""
        input_data = '''\
Display Queue details

Display Queue details
QUEUE(SYSTEM.DEFAULT.LOCAL.QUEUE) \
TYPE(QLOCAL) \
CURDEPTH(0) \
MAXDEPTH(5000)'''
        check_data = {'SYSTEM.DEFAULT.LOCAL.QUEUE': {'curdepth': '0',
                                                     'maxdepth': '5000',
                                                     'type': 'QLOCAL'}}
        self.assertEqual(
            check_data,
            get_queues_labels(queue_labels_data=input_data))

    def test_get_queues_labels_monitor(self):
        """Test for `get_queues_labels_monitor` function."""
        input_data = '''\
Display queue status details
QUEUE(DEV.QUEUE.1) TYPE(QUEUE) \
CURDEPTH(0)        LGETDATE(2019-12-24) \
LGETTIME(13.00.01) LPUTDATE(2019-12-24) \
LPUTTIME(13.00.00) MONQ(MEDIUM) \
MSGAGE(0)          QTIME(3231, 3232)
Display queue status details
QUEUE(DEV.QUEUE.2) TYPE(QUEUE) \
CURDEPTH(0)        LGETDATE(2019-12-24) \
LGETTIME(13.00.02) LPUTDATE(2019-12-24) \
LPUTTIME(13.00.00) MONQ(OFF) \
MSGAGE(0)          QTIME(,)'''
        check_data = {'DEV.QUEUE.1': {'lgettime': '13.00.01',
                                      'lputtime': '13.00.00',
                                      'lgetdate': '2019-12-24',
                                      'lputdate': '2019-12-24',
                                      'msgage': '0',
                                      'qtime': '3231, 3232'}}
        self.assertEqual(
            check_data,
            get_queues_labels_monitor(queue_labels_data=input_data))


class TestMakeMetricsDataForQueues(unittest.TestCase):
    def timestmp(self, d):
        """Returns timestamp."""
        result = time.mktime(datetime.datetime.strptime(d, "%Y-%m-%d %H.%M.%S").timetuple())
        return int(result)

    def test_make_metrics_data_for_queues(self):
        """Test for `make_metrics_data_for_queues` function."""
        mq_manager = 'TEST'
        input_data = {'SYSTEM.DEFAULT.LOCAL.QUEUE': {'curdepth': '0',
                                                     'maxdepth': '5000',
                                                     'type': 'QLOCAL'}}
        check_data = '''\
# HELP mq_queue_curdepth Current depth of queue.
# TYPE mq_queue_curdepth gauge
mq_queue_curdepth{qmname="TEST", queuename="SYSTEM.DEFAULT.LOCAL.QUEUE", type="QLOCAL"} 0
# HELP mq_queue_maxdepth Maximum depth of queue.
# TYPE mq_queue_maxdepth gauge
mq_queue_maxdepth{qmname="TEST", queuename="SYSTEM.DEFAULT.LOCAL.QUEUE", type="QLOCAL"} 5000\n'''
        self.assertEqual(
            check_data,
            make_metrics_data_for_queues(
                queues_labels=input_data,
                mq_manager=mq_manager))

    def test_make_metrics_data_for_queues_monitor(self):
        """Test for `make_metrics_data_for_queues_monitor` function."""
        mq_manager = 'TEST'
        input_data = {'DEV.QUEUE.1': {'lgettime': '13.00.01',
                                      'lputtime': '13.00.00',
                                      'lgetdate': '2019-12-24',
                                      'lputdate': '2019-12-24',
                                      'msgage': '0',
                                      'qtime': '3231, 3232'}}
        check_data = '''\
# HELP mq_queue_lget Timestamp on which the last message was retrieved from the queue.
# TYPE mq_queue_lget gauge
mq_queue_lget{{qmname="TEST", queuename="DEV.QUEUE.1"}} {1}
# HELP mq_queue_lput Timestamp on which the last message was put to the queue.
# TYPE mq_queue_lput gauge
mq_queue_lput{{qmname="TEST", queuename="DEV.QUEUE.1"}} {0}
# HELP mq_queue_msgage Age of the oldest message on the queue.
# TYPE mq_queue_msgage gauge
mq_queue_msgage{{qmname="TEST", queuename="DEV.QUEUE.1"}} 0
# HELP mq_queue_qtime Interval between messages being put on the queue and then being destructively read.
# TYPE mq_queue_qtime gauge
mq_queue_qtime{{qmname="TEST", queuename="DEV.QUEUE.1", indicator="short_term"}} 3231
mq_queue_qtime{{qmname="TEST", queuename="DEV.QUEUE.1", indicator="long_term"}} 3232
'''.format(self.timestmp(d='2019-12-24 13.00.00'),
           self.timestmp(d='2019-12-24 13.00.01'))
        self.assertEqual(
            check_data,
            make_metrics_data_for_queues_monitor(
                queues_labels=input_data,
                mq_manager=mq_manager))


class GetMetricAnnotation(unittest.TestCase):
    def test_get_metric_name(self):
        """Test for `get_metric_name` function."""
        self.assertEqual('mq_queue_status', get_metric_name(metric_label='status'))

    def test_get_metric_annotation(self):
        """Tests for `get_metric_annotation` function."""
        self.assertIsInstance(get_metric_annotation(), dict)
        self.assertIsInstance(get_metric_annotation().get('maxdepth'), list)
        self.assertIsInstance(get_metric_annotation().get('maxdepth')[0], str)
        self.assertIsInstance(get_metric_annotation().get('maxdepth')[1], int)

    def test_get_metric_annotation_monitor(self):
        """Tests for `get_metric_annotation_monitor` function."""
        self.assertIsInstance(get_metric_annotation_monitor(), dict)
        self.assertIsInstance(get_metric_annotation_monitor().get('msgage'), list)
        self.assertIsInstance(get_metric_annotation_monitor().get('msgage')[0], str)
        self.assertIsInstance(get_metric_annotation_monitor().get('msgage')[1], int)


if __name__ == '__main__':
    unittest.main()
