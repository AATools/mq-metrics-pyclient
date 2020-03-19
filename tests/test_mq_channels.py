# -*- coding: utf-8 -*-
import os
import sys
import unittest
from modules.mq_channels import (
    get_channels,
    extract_channel_name,
    get_template,
    get_channel_status,
    format_channel_output,
    make_metric_for_mq_channels_status
    )
sys.path.append(os.getcwd())


class TestGetChannel(unittest.TestCase):
    def test_get_channels(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : display channel (*)
AMQ8414: Display Channel details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)
One MQSC command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        check_data = ['CHANNEL(ADMIN.SVRCONN)']
        self.assertEqual(check_data, get_channels(input_data))


class TestExtractChannelName(unittest.TestCase):
    def test_extract_channel_name(self):
        input_data = 'CHANNEL(ADMIN.SVRCONN)'
        check_data = 'ADMIN.SVRCONN'
        self.assertEqual(check_data, extract_channel_name(input_data))

    def test_hidden_system_cnannel(self):
        input_data = 'CHANNEL(SYSTEM.ADMIN.SVRCONN)'
        self.assertFalse(extract_channel_name(input_data))


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
                    'STATUS': ''
                    }
        self.assertEqual(tempalte, get_template())


class TestGetChannelStatus(unittest.TestCase):
    def test_get_channel_status(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011. ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(TEST.SRVCONN) BATCHES BUFSRCVD BUFSSENT BYTSRCVD BYTSSENT CHSTADA CHSTATI JOBNAME LSTMSGDA LSTMSGTI MSGS
AMQ8417: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   BUFSRCVD(7216)                          BUFSSENT(7215)\n   BYTSRCVD(4894300)                       BYTSSENT(949752)\n   CHSTADA(2020-03-19)                     CHSTATI(18.00.00)\n   CONNAME(127.0.0.1)                      CURRENT\n   JOBNAME(000010EC00000007)               LSTMSGDA(2020-03-19)\n   LSTMSGTI(18.15.01)                      MSGS(1510)\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
One MQSC command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        label_data = [{'BUFSRCVD': '7216',
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
        check_data = [{'BATCHES': '',
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
        self.assertEqual(check_data, get_channel_status(input_data, label_data))

    def test_get_channel_status_not_found(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(TEST.SRVCONN)
AMQ8420: Channel Status not found.\nOne MQSC command read.\nNo commands have a syntax error.\nOne valid MQSC command could not be processed.\n'''
        label_data = [{'ALTDATE': '2017-05-02',
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
        check_data = [{ 'BATCHES': '',
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
        self.assertEqual(check_data, get_channel_status(input_data, label_data))


class TestFormatChannelOutput(unittest.TestCase):
    def test_format_channel_output_one(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(ADMIN.SVRCONN)
AMQ8417: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.1)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
One MQSC command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        check_data = [{'CHANNEL': 'ADMIN.SVRCONN', 'CHLTYPE': 'SVRCONN', 'CONNAME': '127.0.0.1', 'CURRENT': ' ', 'STATUS': 'RUNNING','SUBSTATE': 'RECEIVE'}]
        self.assertEqual(check_data, format_channel_output(input_data))

    def test_format_channel_output_many(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.' \
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(ADMIN.SVRCONN)
AMQ8417: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.1)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
AMQ8417: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.2)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
One MQSC command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        check_data = [
            {'CHANNEL': 'ADMIN.SVRCONN', 'CHLTYPE': 'SVRCONN', 'CONNAME': '127.0.0.1', 'CURRENT': ' ', 'STATUS': 'RUNNING','SUBSTATE': 'RECEIVE'},
            {'CHANNEL': 'ADMIN.SVRCONN', 'CHLTYPE': 'SVRCONN', 'CONNAME': '127.0.0.2', 'CURRENT': ' ', 'STATUS': 'RUNNING','SUBSTATE': 'RECEIVE'}
            ]
        self.assertEqual(check_data, format_channel_output(input_data))

    def test_format_channel_output_not_found_AMQ84_in_first_entry(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(ADMIN.SVRCONN)
AMQ85: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.1)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
AMQ8417: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.2)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
One MQSC command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        check_data = [
        {'CHANNEL': 'ADMIN.SVRCONN', 'CHLTYPE': 'SVRCONN', 'CONNAME': '127.0.0.2', 'CURRENT': ' ', 'STATUS': 'RUNNING','SUBSTATE': 'RECEIVE'}
        ]
        self.assertEqual(check_data, format_channel_output(input_data))

    def test_format_channel_output_not_found_AMQ84_at_all(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(ADMIN.SVRCONN)
AMQ85: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.1)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
AMQ85: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.2)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
One MQSC command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        check_data = [{}]
        self.assertEqual(check_data, format_channel_output(input_data))

    def test_format_channel_output_not_found_OneMQSC(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(ADMIN.SVRCONN)
AMQ8417: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.1)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
One command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        check_data = []
        self.assertEqual(check_data, format_channel_output(input_data))


class TestMakeMetricForMqChannelsStatus(unittest.TestCase):
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
    def test_make_metric_status(self):
            metric_type = 'status'
            check_data = 'mq_channel_status{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", chstada="2020-03-19", chstati="18.00.00", rqmname="", jobname="000010EC00000007", channel="ADMIN.SVRCONN"} 3\n'
            self.assertEqual(check_data, make_metric_for_mq_channels_status(self.channel_data, self.mq_manager, metric_type))


if __name__ == '__main__':
    unittest.main()
