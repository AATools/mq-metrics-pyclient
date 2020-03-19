# -*- coding: utf-8 -*-
import os
import sys
import unittest
from mq_metrics_client import get_mq_channels_metrics
sys.path.append(os.getcwd())


class TestGetMqChannels(unittest.TestCase):
    def test_get_mq_channels_metrics(self):
        mqm = 'TEST'
        input_data = {'ADMIN.SRVCONN':[{'BATCHES': '50',
                                         'BUFSRCVD': '1000',
                                         'BUFSSENT': '1100',
                                         'BYTSRCVD': '4894300',
                                         'BYTSSENT': '949752',
                                         'CHANNEL': 'TEST',
                                         'CHLTYPE': 'SVR',
                                         'CHSTADA': '2020-03-19',
                                         'CHSTATI': '17.00.00',
                                         'CONNAME': '10.92.10.10(1414)',
                                         'JOBNAME': '00005C6800000001',
                                         'LSTMSGDA': '2020-03-19',
                                         'LSTMSGTI': '18.30.01',
                                         'MSGS': '50',
                                         'RQMNAME': 'TEST',
                                         'STATUS': 'RUNNING',
                                         'SUBSTATE': 'MQGET',
                                         'XMITQ': 'TEST'},
                                       {'BATCHES': '',
                                         'BUFSRCVD': '7216',
                                         'BUFSSENT': '7215',
                                         'BYTSRCVD': '4894300',
                                         'BYTSSENT': '949752',
                                         'CHANNEL': 'ADMIN.SVRCONN',
                                         'CHLTYPE': 'SVRCONN',
                                         'CHSTADA': '2020-03-19',
                                         'CHSTATI': '18.00.00',
                                         'CONNAME': '127.0.0.1',
                                         'JOBNAME': '000010EC00000007',
                                         'LSTMSGDA': '2020-03-19',
                                         'LSTMSGTI': '18.15.01',
                                         'MSGS': '1510',
                                         'RQMNAME': '',
                                         'STATUS': 'RUNNING',
                                         'SUBSTATE': 'RECEIVE',
                                         'XMITQ': ''}]}
        check_data = '''mq_channel_status{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", jobname="00005C6800000001", channel="TEST"} 3
mq_channel_buffers{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", indicator="buffers_received", jobname="00005C6800000001", channel="TEST"} 1000
mq_channel_buffers{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", indicator="buffers_sent", jobname="00005C6800000001", channel="TEST"} 1100
mq_channel_bytes{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", indicator="bytes_received", jobname="00005C6800000001", channel="TEST"} 4894300
mq_channel_bytes{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", indicator="bytes_sent", jobname="00005C6800000001", channel="TEST"} 949752
mq_channel_lmsg{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", jobname="00005C6800000001", channel="TEST"} 1584631801
mq_channel_msgs{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", jobname="00005C6800000001", channel="TEST"} 50
mq_channel_batches{qmname="TEST", conname="10.92.10.10(1414)", substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", chstati="17.00.00", rqmname="TEST", jobname="00005C6800000001", channel="TEST"} 50
mq_channel_status{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 3
mq_channel_buffers{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", indicator="buffers_received", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 7216
mq_channel_buffers{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", indicator="buffers_sent", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 7215
mq_channel_bytes{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", indicator="bytes_received", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 4894300
mq_channel_bytes{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", indicator="bytes_sent", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 949752
mq_channel_lmsg{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 1584630901
mq_channel_msgs{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 1510
mq_channel_batches{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 0\n'''
        self.assertEqual(check_data, get_mq_channels_metrics(input_data, mqm))



if __name__ == '__main__':
    unittest.main()
