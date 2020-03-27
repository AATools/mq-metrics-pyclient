# -*- coding: utf-8 -*-
import os
import sys
import unittest
import time
import datetime
from mq_metrics_client import get_mq_channels_metrics
sys.path.append(os.getcwd())


class TestGetMqChannels(unittest.TestCase):
    def timestmp(self, d, t):
        result = time.mktime(datetime.datetime.strptime(
          ' '.join([d, t]), "%Y-%m-%d %H.%M.%S").timetuple())
        return int(result)

    def test_get_mq_channels_metrics(self):
        mqm = 'TEST'
        input_data = {'ADMIN.SRVCONN': [{'BATCHES': '50',
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
        templ = ['qmname="TEST", conname="10.92.10.10(1414)", \
substate="MQGET", xmitq="TEST", chltype="SVR", chstada="2020-03-19", \
chstati="17.00.00", rqmname="TEST",',
                 'qmname="TEST", conname="127.0.0.1", \
substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", \
chstati="18.00.00", rqmname="",']
        check_data = '''\
mq_channel_status{{{0} jobname="00005C6800000001", channel="TEST"}} 3
mq_channel_buffers{{{0} indicator="buffers_received", \
jobname="00005C6800000001", channel="TEST"}} 1000
mq_channel_buffers{{{0} indicator="buffers_sent", \
jobname="00005C6800000001", channel="TEST"}} 1100
mq_channel_bytes{{{0} indicator="bytes_received", \
jobname="00005C6800000001", channel="TEST"}} 4894300
mq_channel_bytes{{{0} indicator="bytes_sent", \
jobname="00005C6800000001", channel="TEST"}} 949752
mq_channel_lmsg{{{0} jobname="00005C6800000001", \
channel="TEST"}} {2}
mq_channel_msgs{{{0} jobname="00005C6800000001", \
channel="TEST"}} 50
mq_channel_batches{{{0} \
jobname="00005C6800000001", channel="TEST"}} 50
mq_channel_status{{{1} \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 3
mq_channel_buffers{{{1} indicator="buffers_received", \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 7216
mq_channel_buffers{{{1} indicator="buffers_sent", \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 7215
mq_channel_bytes{{{1} indicator="bytes_received", \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 4894300
mq_channel_bytes{{{1} indicator="bytes_sent", \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 949752
mq_channel_lmsg{{{1} \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} {3}
mq_channel_msgs{{{1} \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 1510
mq_channel_batches{{{1} \
jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 0\n\
'''.format(templ[0],
           templ[1],
           self.timestmp(input_data['ADMIN.SRVCONN'][0]['LSTMSGDA'],
                         input_data['ADMIN.SRVCONN'][0]['LSTMSGTI']),
           self.timestmp(input_data['ADMIN.SRVCONN'][1]['LSTMSGDA'],
                         input_data['ADMIN.SRVCONN'][1]['LSTMSGTI']))
        self.assertEqual(
            check_data,
            get_mq_channels_metrics(
                input_data,
                mqm))


if __name__ == '__main__':
    unittest.main()
