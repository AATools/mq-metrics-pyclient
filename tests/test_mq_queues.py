# -*- coding: utf-8 -*-
import os
import sys
import unittest
from modules.mq_queues import (
    make_metrics_data_for_queues,
    get_queues_labels
    )
sys.path.append(os.getcwd())


class TestGetQueuesLables(unittest.TestCase):
    def test_get_queues_labels(self):
        input_data = 'QUEUE(SYSTEM.DEFAULT.LOCAL.QUEUE) TYPE(QLOCAL)   CURDEPTH(0)  MAXDEPTH(5000)'
        check_data = {'SYSTEM.DEFAULT.LOCAL.QUEUE': {'curdepth': '0',
                                                     'maxdepth': '5000',
                                                     'type': 'QLOCAL'}}
        self.assertEqual(check_data,  get_queues_labels(input_data))


class TestMakeMetricsDataForQueues(unittest.TestCase):
    def test_make_metrics_data_for_queues(self):
        mq_manager = 'TEST'
        input_data = {'SYSTEM.DEFAULT.LOCAL.QUEUE': {'curdepth': '0',
                                                     'maxdepth': '5000',
                                                     'type': 'QLOCAL'}}
        check_data = '''mq_queue_maxdepth{qmname="TEST", queuename="SYSTEM.DEFAULT.LOCAL.QUEUE", type="QLOCAL"} 5000
mq_queue_curdepth{qmname="TEST", queuename="SYSTEM.DEFAULT.LOCAL.QUEUE", type="QLOCAL"} 0\n'''
        self.assertEqual(check_data, make_metrics_data_for_queues(input_data, mq_manager))


if __name__ == '__main__':
    unittest.main()
