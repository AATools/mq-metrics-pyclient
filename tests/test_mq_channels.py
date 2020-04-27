# -*- coding: utf-8 -*-
import os
import sys
import unittest
import time
import datetime
from modules.mq_channels import (
    get_channels,
    extract_channel_name,
    get_template,
    get_channel_status,
    format_channel_output,
    make_metric_for_mq_channels_status)
sys.path.append(os.getcwd())


class TestGetChannel(unittest.TestCase):
    def test_get_channels(self):
        input_data = '''\
5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : display channel (*)
AMQ8414: Display Channel details.
   CHANNEL(ADMIN.SVRCONN)     CHLTYPE(SVRCONN)
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''
        check_data = ['CHANNEL(ADMIN.SVRCONN)']
        self.assertEqual(
            check_data,
            get_channels(input_data))


class TestExtractChannelName(unittest.TestCase):
    def test_extract_channel_name(self):
        input_data = 'CHANNEL(ADMIN.SVRCONN)'
        check_data = 'ADMIN.SVRCONN'
        self.assertEqual(
            check_data,
            extract_channel_name(input_data))

    def test_hidden_system_cnannel(self):
        input_data = 'CHANNEL(SYSTEM.ADMIN.SVRCONN)'
        self.assertFalse(
            extract_channel_name(input_data))


class TestGetTemplate(unittest.TestCase):
    def test_get_template(self):
        tempalte = {'BATCHES': '',
                    'BUFSRCVD': '',
                    'BUFSSENT': '',
                    'BYTSRCVD': '',
                    'BYTSSENT': '',
                    'CHANNEL': '',
                    'CHLTYPE': '',
                    'CHSTADA': '',
                    'CHSTATI': '',
                    'CONNAME': '',
                    'JOBNAME': '',
                    'LSTMSGDA': '',
                    'LSTMSGTI': '',
                    'MSGS': '',
                    'RQMNAME': '',
                    'XMITQ': '',
                    'SUBSTATE': '',
                    'STATUS': ''}
        self.assertEqual(
            tempalte,
            get_template())


class TestGetChannelStatus(unittest.TestCase):
    input_header = '''
5724-H72 (C) Copyright IBM Corp. 1994, 2011. ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : dis chstatus(ADMIN.SRVCONN) BATCHES BUFSRCVD \
BUFSSENT BYTSRCVD BYTSSENT CHSTADA CHSTATI JOBNAME \
LSTMSGDA LSTMSGTI MSGS
'''
    input_temp = ['''\
   CHANNEL(ADMIN.SVRCONN)     CHLTYPE(SVRCONN)
   BUFSRCVD(7216)             BUFSSENT(7215)
   BYTSRCVD(4894300)          BYTSSENT(949752)
   CHSTADA(2020-03-19)        CHSTATI(18.00.00)
   CONNAME(127.0.0.1)         CURRENT
   JOBNAME(000010EC00000007)  LSTMSGDA(2020-03-19)
   LSTMSGTI(18.15.01)         MSGS(1510)
   STATUS(RUNNING)            SUBSTATE(RECEIVE)''']

    def test_get_channel_status(self):
        input_data = '''\
{0}
AMQ8417: Display Channel Status details.
{1}
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''.format(self.input_header,
           self.input_temp[0])
        label_data = [
            {'BUFSRCVD': '7216',
             'BUFSSENT': '7215',
             'BYTSRCVD': '4894300',
             'BYTSSENT': '949752',
             'CHANNEL': 'ADMIN.SVRCONN',
             'CHLTYPE': 'SVRCONN',
             'CHSTADA': '2020-03-19',
             'CHSTATI': '18.00.00',
             'CONNAME': '127.0.0.1',
             'CURRENT': ' ',
             'JOBNAME': '000010EC00000007',
             'LSTMSGDA': '2020-03-19',
             'LSTMSGTI': '18.15.01',
             'MSGS': '1510',
             'STATUS': 'RUNNING',
             'SUBSTATE': 'RECEIVE'}]
        check_data = [
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
             'XMITQ': ''}]
        self.assertEqual(
            check_data,
            get_channel_status(
                input_data,
                label_data))

    def test_get_channel_status_not_found(self):
        input_data = '''\
{0}
AMQ8420: Channel Status not found.
One MQSC command read.
No commands have a syntax error.
One valid MQSC command could not be processed.
'''.format(self.input_header)
        label_data = [
            {'ALTDATE': '2017-05-02',
             'ALTTIME': '11.22.47',
             'CHANNEL': 'TEST.SVRCONN',
             'CHLTYPE': 'SVRCONN',
             'COMPHDR': 'NONE',
             'COMPMSG': 'NONE',
             'DESCR': ' ',
             'DISCINT': '0',
             'HBINT': '300',
             'KAINT': 'AUTO',
             'MAXINST': '999999999',
             'MAXINSTC': '999999999',
             'MAXMSGL': '4194304',
             'MCAUSER': ' ',
             'MONCHL': 'QMGR',
             'RCVDATA': ' ',
             'RCVEXIT': ' ',
             'SCYDATA': ' ',
             'SCYEXIT': ' ',
             'SENDDATA': ' ',
             'SENDEXIT': ' ',
             'SHARECNV': '10',
             'SSLCAUTH': 'REQUIRED',
             'SSLCIPH': ' ',
             'SSLPEER': ' ',
             'TRPTYPE': 'TCP'}]
        check_data = [
            {'BATCHES': '',
             'BUFSRCVD': '',
             'BUFSSENT': '',
             'BYTSRCVD': '',
             'BYTSSENT': '',
             'CHANNEL': 'TEST.SVRCONN',
             'CHLTYPE': 'SVRCONN',
             'CHSTADA': '',
             'CHSTATI': '',
             'CONNAME': '',
             'JOBNAME': '',
             'LSTMSGDA': '',
             'LSTMSGTI': '',
             'MSGS': '',
             'RQMNAME': '',
             'XMITQ': '',
             'SUBSTATE': '',
             'STATUS': ''}]
        self.assertEqual(
            check_data,
            get_channel_status(
                input_data,
                label_data))


class TestFormatChannelOutput(unittest.TestCase):
    input_header = '''
5724-H72 (C) Copyright IBM Corp. 1994, 2011. ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.
     1 : dis chstatus(ADMIN.SRVCONN) BATCHES BUFSRCVD \
BUFSSENT BYTSRCVD BYTSSENT CHSTADA CHSTATI JOBNAME \
LSTMSGDA LSTMSGTI MSGS
'''
    input_temp = ['''\
   CHANNEL(ADMIN.SVRCONN)     CHLTYPE(SVRCONN)
   BUFSRCVD(7216)             BUFSSENT(7215)
   BYTSRCVD(4894300)          BYTSSENT(949752)
   CHSTADA(2020-03-19)        CHSTATI(18.00.00)
   CONNAME(127.0.0.1)         CURRENT
   JOBNAME(000010EC00000007)  LSTMSGDA(2020-03-19)
   LSTMSGTI(18.15.01)         MSGS(1510)
   STATUS(RUNNING)            SUBSTATE(RECEIVE)''',
                  '''\
   CHANNEL(ADMIN.SVRCONN)     CHLTYPE(SVRCONN)
   BUFSRCVD(8000)             BUFSSENT(8000)
   BYTSRCVD(4895500)          BYTSSENT(980752)
   CHSTADA(2020-03-20)        CHSTATI(18.00.00)
   CONNAME(127.0.0.2)         CURRENT
   JOBNAME(000020EC00000007)  LSTMSGDA(2020-03-20)
   LSTMSGTI(19.00.01)         MSGS(2000)
   STATUS(RUNNING)            SUBSTATE(RECEIVE)''']
    check_data_temp = [
        {'BUFSRCVD': '7216',
         'BUFSSENT': '7215',
         'BYTSRCVD': '4894300',
         'BYTSSENT': '949752',
         'CHANNEL': 'ADMIN.SVRCONN',
         'CHLTYPE': 'SVRCONN',
         'CHSTADA': '2020-03-19',
         'CHSTATI': '18.00.00',
         'CONNAME': '127.0.0.1',
         'CURRENT': ' ',
         'JOBNAME': '000010EC00000007',
         'LSTMSGDA': '2020-03-19',
         'LSTMSGTI': '18.15.01',
         'MSGS': '1510',
         'STATUS': 'RUNNING',
         'SUBSTATE': 'RECEIVE'},
        {'BUFSRCVD': '8000',
         'BUFSSENT': '8000',
         'BYTSRCVD': '4895500',
         'BYTSSENT': '980752',
         'CHANNEL': 'ADMIN.SVRCONN',
         'CHLTYPE': 'SVRCONN',
         'CHSTADA': '2020-03-20',
         'CHSTATI': '18.00.00',
         'CONNAME': '127.0.0.2',
         'CURRENT': ' ',
         'JOBNAME': '000020EC00000007',
         'LSTMSGDA': '2020-03-20',
         'LSTMSGTI': '19.00.01',
         'MSGS': '2000',
         'STATUS': 'RUNNING',
         'SUBSTATE': 'RECEIVE'}]

    def test_format_channel_output_one(self):
        input_data = '''\
{0}
AMQ8417: Display Channel Status details.
{1}
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''.format(self.input_header,
           self.input_temp[0])
        check_data = [self.check_data_temp[0]]
        self.assertEqual(
            check_data,
            format_channel_output(input_data))

    def test_format_channel_output_many(self):
        input_data = '''\
{0}
AMQ8417: Display Channel Status details.
{1}
AMQ8417: Display Channel Status details.
{2}
One MQSC command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''.format(self.input_header,
           self.input_temp[0],
           self.input_temp[1])
        check_data = [
            self.check_data_temp[0],
            self.check_data_temp[1]]
        self.assertEqual(
            check_data,
            format_channel_output(input_data))

    def test_format_channel_output_not_found_AMQ84_in_first_entry(self):
        input_data = '''\
{0}
AMQ85: Display Channel Status details.
{1}
AMQ8417: Display Channel Status details.
{2}
One MQSC command read.\nNo commands have a syntax error.
All valid MQSC commands were processed.
'''.format(self.input_header,
           self.input_temp[0],
           self.input_temp[1])
        check_data = [self.check_data_temp[1]]
        self.assertEqual(
            check_data,
            format_channel_output(input_data))

    def test_format_channel_output_not_found_AMQ84_at_all(self):
        input_data = '''\
{0}
AMQ85: Display Channel Status details.
{1}
AMQ85: Display Channel Status details.
{2}
One MQSC command read.\nNo commands have a syntax error.
All valid MQSC commands were processed.
'''.format(self.input_header,
           self.input_temp[0],
           self.input_temp[1])
        check_data = [{}]
        self.assertEqual(
            check_data,
            format_channel_output(input_data))

    def test_format_channel_output_not_found_OneMQSC(self):
        input_data = '''\
{0}
AMQ8417: Display Channel Status details.
{1}
One command read.
No commands have a syntax error.
All valid MQSC commands were processed.
'''.format(self.input_header,
           self.input_temp[0])
        check_data = []
        self.assertEqual(
            check_data,
            format_channel_output(input_data))


class TestMakeMetricForMqChannelsStatus(unittest.TestCase):
    def timestmp(self, d, t):
        result = time.mktime(datetime.datetime.strptime(
            ' '.join([d, t]), "%Y-%m-%d %H.%M.%S").timetuple())
        return int(result)

    def test_make_metric(self):
        mq_manager = 'TEST'
        channel_data = {'BATCHES': '',
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
                        'XMITQ': ''}
        data_templ = '''qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", \
chstada="2020-03-19", chstati="18.00.00", rqmname=""'''
        check_data_temp = ['''\
# HELP mq_channel_status Current status of MQ channel.
# TYPE mq_channel_status gauge
mq_channel_status{{{0}, jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 3
'''.format(data_templ), '''\
# HELP mq_channel_buffers Number of transmission buffers received and sent.
# TYPE mq_channel_buffers counter
mq_channel_buffers{{{0}, indicator="buffers_received", jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 7216
'''.format(data_templ), '''\
# HELP mq_channel_buffers Number of transmission buffers received and sent.
# TYPE mq_channel_buffers counter
mq_channel_buffers{{{0}, indicator="buffers_sent", jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 7215
'''.format(data_templ), '''\
# HELP mq_channel_bytes Number of bytes received and sent during this session.
# TYPE mq_channel_bytes counter
mq_channel_bytes{{{0}, indicator="bytes_received", jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 4894300
'''.format(data_templ), '''\
# HELP mq_channel_bytes Number of bytes received and sent during this session.
# TYPE mq_channel_bytes counter
mq_channel_bytes{{{0}, indicator="bytes_sent", jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 949752
'''.format(data_templ), '''\
# HELP mq_channel_lmsg Timestamp on which the last message was sent or MQI call was handled.
# TYPE mq_channel_lmsg gauge
mq_channel_lmsg{{{0}, jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} {1}
'''.format(data_templ,
           self.timestmp(channel_data['LSTMSGDA'],
                         channel_data['LSTMSGTI'])), '''\
# HELP mq_channel_msgs Number of messages sent or received during this session.
# TYPE mq_channel_msgs counter
mq_channel_msgs{{{0}, jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 1510
'''.format(data_templ), '''\
# HELP mq_channel_batches Number of completed batches during this session.
# TYPE mq_channel_batches counter
mq_channel_batches{{{0}, jobname="000010EC00000007", channel="ADMIN.SVRCONN"}} 0
'''.format(data_templ)]
        status_data_temp = ['status',
                            'buffers_received',
                            'buffers_sent',
                            'bytes_received',
                            'bytes_sent',
                            'lmsg',
                            'msgs',
                            'batches']
        self.assertEqual(
            len(check_data_temp),
            len(status_data_temp))
        for i in range(len(status_data_temp)):
            self.assertEqual(
                check_data_temp[i],
                make_metric_for_mq_channels_status(
                    channel_data,
                    mq_manager,
                    status_data_temp[i]))


if __name__ == '__main__':
    unittest.main()
