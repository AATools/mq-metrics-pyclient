# -*- coding: utf-8 -*-
import os
import sys
import unittest
import time
import datetime
from modules.mq_queues import (
    make_metrics_data_for_queues,
    get_queues_labels,
    make_metrics_data_for_queues_monitor,
    get_queues_labels_monitor)
sys.path.append(os.getcwd())


class TestGetQueuesLabels(unittest.TestCase):
    def test_get_queues_labels(self):
        input_data = '''\
QUEUE(SYSTEM.DEFAULT.LOCAL.QUEUE) \
TYPE(QLOCAL) \
CURDEPTH(0) \
MAXDEPTH(5000)'''
        check_data = {'SYSTEM.DEFAULT.LOCAL.QUEUE': {'curdepth': '0',
                                                     'maxdepth': '5000',
                                                     'type': 'QLOCAL'}}
        self.assertEqual(
            check_data,
            get_queues_labels(input_data))


class TestMakeMetricsDataForQueues(unittest.TestCase):
    def test_make_metrics_data_for_queues(self):
        mq_manager = 'TEST'
        input_data = {'SYSTEM.DEFAULT.LOCAL.QUEUE': {'curdepth': '0',
                                                     'maxdepth': '5000',
                                                     'type': 'QLOCAL'}}
        check_data = '''\
mq_queue_maxdepth{qmname="TEST", queuename="SYSTEM.DEFAULT.LOCAL.QUEUE", \
type="QLOCAL"} 5000
mq_queue_curdepth{qmname="TEST", queuename="SYSTEM.DEFAULT.LOCAL.QUEUE", \
type="QLOCAL"} 0\n'''
        self.assertEqual(
            check_data,
            make_metrics_data_for_queues(
                input_data,
                mq_manager))


class TestGetQueuesLabelsMonitor(unittest.TestCase):
    def test_get_queues_labels_monitor(self):
        input_data = '''\
QUEUE(DEV.QUEUE.1) TYPE(QUEUE) \
CURDEPTH(0)        LGETDATE(2019-12-24) \
LGETTIME(13.00.01) LPUTDATE(2019-12-24) \
LPUTTIME(13.00.00) MONQ(MEDIUM) \
MSGAGE(0)          QTIME(3231, 3232)'''
        check_data = {'DEV.QUEUE.1': {'lgettime': '13.00.01',
                                      'lputtime': '13.00.00',
                                      'lgetdate': '2019-12-24',
                                      'lputdate': '2019-12-24',
                                      'msgage': '0',
                                      'qtime': '3231, 3232'}}
        self.assertEqual(
            check_data,
            get_queues_labels_monitor(input_data))


class TestMakeMetricsDataForQueuesMonitor(unittest.TestCase):
    def timestmp(self, d):
        result = time.mktime(datetime.datetime.strptime(
            d, "%Y-%m-%d %H.%M.%S").timetuple())
        return int(result)

    def test_make_metrics_data_for_queues_monitor(self):
        mq_manager = 'TEST'
        input_data = {'DEV.QUEUE.1': {'lgettime': '13.00.01',
                                      'lputtime': '13.00.00',
                                      'lgetdate': '2019-12-24',
                                      'lputdate': '2019-12-24',
                                      'msgage': '0',
                                      'qtime': '3231, 3232'}}
        check_data = '''\
mq_queue_msgage{{qmname="TEST", \
queuename="DEV.QUEUE.1"}} 0
mq_queue_lput{{qmname="TEST", \
queuename="DEV.QUEUE.1"}} {0}
mq_queue_lget{{qmname="TEST", \
queuename="DEV.QUEUE.1"}} {1}
mq_queue_qtime{{qmname="TEST", \
queuename="DEV.QUEUE.1", indicator="short_term"}} 3231
mq_queue_qtime{{qmname="TEST", \
queuename="DEV.QUEUE.1", indicator="long_term"}} 3232
'''.format(self.timestmp('2019-12-24 13.00.00'),
           self.timestmp('2019-12-24 13.00.01'))
        self.assertEqual(
            check_data,
            make_metrics_data_for_queues_monitor(
                input_data,
                mq_manager))


if __name__ == '__main__':
    unittest.main()
