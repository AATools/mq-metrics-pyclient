# -*- coding: utf-8 -*-
"""Tests for `mq_listener`."""
import os
import sys
import unittest
from modules.mq_listener import (
    get_listeners,
    format_output,
    make_metric_for_mq_listener_status,
    get_listener_labels,
    get_listener_status,
    get_metric_name,
    get_metric_annotation)
sys.path.append(os.getcwd())


class TestGetListeners(unittest.TestCase):
    def test_get_listeners(self):
        """Test for `get_listeners` function."""
        input_data = '''\
5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : display listener(*)
AMQ8630: Display listener information details.
   LISTENER(LISTENER)
AMQ8630: Display listener information details.
   LISTENER(SYSTEM.DEFAULT.LISTENER.TCP)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''
        check_data = ['LISTENER']
        self.assertEqual(
            check_data,
            get_listeners(listeners_data=input_data))

    def test_get_listeners_for_defaul_listener(self):
        """Test for `get_listeners` function for `SYSTEM DEFAULT` listener."""
        input_data = '''\
5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : display listener(*)
AMQ8630: Display listener information details.
   LISTENER(SYSTEM.DEFAULT.LISTENER.TCP)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''
        check_data = []
        self.assertEqual(
            check_data,
            get_listeners(listeners_data=input_data))


class TestGetListenerLabels(unittest.TestCase):
    def test_get_listener_labels(self):
        """Test for `get_listener_labels` function."""
        input_data = '''\
5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : display listener(LISTENER)
AMQ8630: Display listener information details.
   LISTENER(LISTENER)     CONTROL(QMGR)
   TRPTYPE(TCP)           PORT(1414)
   IPADDR( )              BACKLOG(0)
   DESCR( )               ALTDATE(2013-12-19)
   ALTTIME(16.34.18)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''
        check_data = {'ALTDATE': '2013-12-19',
                      'ALTTIME': '16.34.18',
                      'BACKLOG': '0',
                      'CONTROL': 'QMGR',
                      'DESCR': ' ',
                      'IPADDR': ' ',
                      'LISTENER': 'LISTENER',
                      'PORT': '1414',
                      'TRPTYPE': 'TCP'}
        self.assertEqual(
            check_data,
            get_listener_labels(labels=input_data))


class TestFormatOutput(unittest.TestCase):
    def test_format_output_status(self):
        """Test for `format_output` function for `status` method."""
        input_data = '''\
724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : dis lsstatus (LISTENER)
AMQ8631: Display listener status details.
   LISTENER(LISTENER)     STATUS(RUNNING)
   PID(11111)             STARTDA(2019-09-03)
   STARTTI(17.47.32)      DESCR( )
   TRPTYPE(TCP)           CONTROL(QMGR)
   IPADDR(*)              PORT(1414)
   BACKLOG(10000)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''
        check_data = {'BACKLOG': '10000',
                      'CONTROL': 'QMGR',
                      'DESCR': ' ',
                      'IPADDR': '*',
                      'LISTENER': 'LISTENER',
                      'PID': '11111',
                      'PORT': '1414',
                      'STARTDA': '2019-09-03',
                      'STARTTI': '17.47.32',
                      'STATUS': 'RUNNING',
                      'TRPTYPE': 'TCP'
                      }
        method = 'status'
        self.assertEqual(
            check_data,
            format_output(data_to_format=input_data, method=method))

    def test_format_output_labels(self):
        """Test for `format_output` function for `labels` method."""
        input_data = '''\
724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : dis lsstatus (LISTENER)
AMQ8631: Display listener status details.
   LISTENER(LISTENER)     STATUS(RUNNING)
   PID(11111)             STARTDA(2019-09-03)
   STARTTI(17.47.32)      DESCR( )
   TRPTYPE(TCP)           CONTROL(QMGR)
   IPADDR(*)              PORT(1414)
   BACKLOG(10000)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''
        check_data = {'CONTROL': 'QMGR',
                      'DESCR': ' ',
                      'IPADDR': '*',
                      'LISTENER': 'LISTENER',
                      'PID': '11111',
                      'PORT': '1414',
                      'STARTDA': '2019-09-03',
                      'STARTTI': '17.47.32',
                      'STATUS': 'RUNNING',
                      'TRPTYPE': 'TCP'
                      }
        method = 'labels'
        self.assertEqual(
            check_data,
            format_output(data_to_format=input_data, method=method))


class TestGetListenerStatus(unittest.TestCase):
    input_labels = '''\
5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : display listener(LISTENER)
AMQ8630: Display listener information details.
   LISTENER(LISTENER)     CONTROL(QMGR)
   TRPTYPE(TCP)           PORT(1414)
   IPADDR( )              BACKLOG(0)
   DESCR( )               ALTDATE(2013-12-19)
   ALTTIME(16.34.18)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''

    def test_get_listener_status(self):
        """Test for `get_listener_status` function."""
        status_dict = {'STOPPED': 0,
                       'RUNNING': 3,
                       }
        for status in status_dict:
            status_name = status
            status_code = status_dict[status]
            input_data = '''\
5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : dis lsstatus(LISTENER)
AMQ8631: Display listener status details.
   LISTENER(LISTENER)     STATUS({0})
   PID(11111)             STARTDA(2019-09-27)
   STARTTI(12.22.31)      DESCR( )
   TRPTYPE(TCP)           CONTROL(QMGR)
   IPADDR(*)              PORT(1414)
   BACKLOG(10000)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
''' .format(status_name)
            check_data = {'BACKLOG': '10000',
                          'CONTROL': 'QMGR',
                          'DESCR': ' ',
                          'IPADDR': '*',
                          'LISTENER': 'LISTENER',
                          'PID': '11111',
                          'PORT': '1414',
                          'STARTDA': '2019-09-27',
                          'STARTTI': '12.22.31',
                          'STATUS': status_code,
                          'TRPTYPE': 'TCP'}
            self.assertEqual(
                check_data,
                get_listener_status(
                    listener_data=input_data,
                    listener_labels=self.input_labels))

    def test_get_listener_status_not_found(self):
        """Test for `get_listener_status` function for `not found` case."""
        input_data = '''\
5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : dis lsstatus(LISTENER)
AMQ8147: WebSphere MQ object LISTENER not found.\nOne MQSC command read.
No commands have a syntax error.
One valid MQSC command could not be processed.
'''
        check_data = {'ALTDATE': '2013-12-19',
                      'ALTTIME': '16.34.18',
                      'BACKLOG': '0',
                      'CONTROL': 'QMGR',
                      'DESCR': ' ',
                      'IPADDR': ' ',
                      'LISTENER': 'LISTENER',
                      'PID': '',
                      'PORT': '1414',
                      'STARTDA': '',
                      'STARTTI': '',
                      'STATUS': 0,
                      'TRPTYPE': 'TCP'}
        self.assertEqual(
            check_data,
            get_listener_status(
                listener_data=input_data,
                listener_labels=self.input_labels))


class TestMakeMetricForMqListenerStatus(unittest.TestCase):
    mqm = 'TEST'

    def test_make_metric_for_mq_listener_status(self):
        """Test for `make_metric_for_mq_listener_status` function."""
        input_data = {'BACKLOG': '10000',
                      'CONTROL': 'QMGR',
                      'DESCR': ' ',
                      'IPADDR': '*',
                      'LISTENER': 'LISTENER',
                      'PID': '11111',
                      'PORT': '1414',
                      'STARTDA': '2019-09-03',
                      'STARTTI': '17.47.32',
                      'STATUS': 3,
                      'TRPTYPE': 'TCP'}
        check_data = '''\
mq_listener_status{qmname="TEST", listener="LISTENER", pid="11111", \
ipadd="*", port="1414", trptype="TCP", control="QMGR", backlog="10000", \
startda="2019-09-03", startti="17.47.32", desc=" "} 3\n'''
        self.assertEqual(
            check_data,
            make_metric_for_mq_listener_status(
                mq_listener_status_data=input_data,
                mqm=self.mqm))


class GetMetricAnnotation(unittest.TestCase):
    def test_get_metric_name(self):
        """Test for `get_metric_name` function."""
        self.assertEqual('mq_listener_status', get_metric_name(metric_label='status'))

    def test_get_metric_annotation(self):
        """Tests for `get_metric_annotation` function."""
        self.assertIsInstance(get_metric_annotation(), dict)
        self.assertIsInstance(get_metric_annotation().get('status'), str)


if __name__ == '__main__':
    unittest.main()
