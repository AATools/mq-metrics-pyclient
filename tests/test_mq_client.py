# -*- coding: utf-8 -*-
import os
import sys
import unittest
from mq_metrics_client import get_mq_channels_metrics
sys.path.append(os.getcwd())


class TestGetMqChannels(unittest.TestCase):
    def test_get_mq_channels_metrics(self):
        mqm = 'TEST'
        input_data = [[({'CHANNEL': 'TEST',
                         'CHLTYPE': 'SVR',
                         'CONNAME': '10.92.10.10(1414)',
                         'RQMNAME': 'TEST',
                         'STATUS': 'RUNNING',
                         'SUBSTATE': 'MQGET',
                         'XMITQ': 'TEST'},
                        1)],
                      [({'CHANNEL': 'ADMIN.SVRCONN',
                         'CHLTYPE': 'SVRCONN',
                         'CONNAME': '127.0.0.1',
                         'RQMNAME': '',
                         'STATUS': 'RUNNING',
                         'SUBSTATE': 'RECEIVE',
                         'XMITQ': ''},
                        5)]]
        check_data = '''mq_channel_connection_count{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", rqmname="TEST", channel="TEST"} 1
mq_channel_status{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", rqmname="TEST", channel="TEST"} 3
mq_channel_connection_count{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", rqmname="", channel="ADMIN.SVRCONN"} 5
mq_channel_status{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", rqmname="", channel="ADMIN.SVRCONN"} 3\n'''
        self.assertEqual(check_data, get_mq_channels_metrics(input_data, mqm))


if __name__ == '__main__':
    unittest.main()
