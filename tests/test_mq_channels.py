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
        tempalte = {'CHANNEL': '',
                    'CHLTYPE': '',
                    'CONNAME': '',
                    'RQMNAME': '',
                    'XMITQ': '',
                    'SUBSTATE': '',
                    'STATUS': ''
                    }
        self.assertEqual(tempalte, get_template())


class TestGetChannelStatus(unittest.TestCase):
    def test_get_channel_status(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(ADMIN.SVRCONN)
AMQ8417: Display Channel Status details.\n   CHANNEL(ADMIN.SVRCONN)                 CHLTYPE(SVRCONN)\n   CONNAME(127.0.0.1)                      CURRENT\n   STATUS(RUNNING)                         SUBSTATE(RECEIVE)
One MQSC command read.\nNo commands have a syntax error.\nAll valid MQSC commands were processed.\n'''
        lable_data = [{'CHANNEL': 'ADMIN.SVRCONN',
                       'CHLTYPE': 'SVRCONN',
                       'CONNAME': '127.0.0.1',
                       'CURRENT': ' ',
                       'STATUS': 'RUNNING',
                       'SUBSTATE': 'RECEIVE'}]
        check_data = [{'CHANNEL': 'ADMIN.SVRCONN',
                       'CHLTYPE': 'SVRCONN',
                       'CONNAME': '127.0.0.1',
                       'RQMNAME': '',
                       'STATUS': 'RUNNING',
                       'SUBSTATE': 'RECEIVE',
                       'XMITQ': ''}]
        self.assertEqual(check_data, get_channel_status(input_data, lable_data))

    def test_get_channel_status_not_found(self):
        input_data = '''5724-H72 (C) Copyright IBM Corp. 1994, 2011.  ALL RIGHTS RESERVED.
Starting MQSC for queue manager TEST.\n\n\n     1 : dis chstatus(TEST.SRVCONN)
AMQ8420: Channel Status not found.\nOne MQSC command read.\nNo commands have a syntax error.\nOne valid MQSC command could not be processed.\n'''
        lable_data = [{'ALTDATE': '2017-05-02',
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
        check_data = [{'CHANNEL': 'TEST.SVRCONN',
                       'CHLTYPE': 'SVRCONN',
                       'CONNAME': '',
                       'RQMNAME': '',
                       'STATUS': '',
                       'SUBSTATE': '',
                       'XMITQ': ''}]
        self.assertEqual(check_data, get_channel_status(input_data, lable_data))


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
    def test_make_metric_connection_count(self):
        channel_data = {'CHANNEL': 'ADMIN.SVRCONN',
                        'CHLTYPE': 'SVRCONN',
                        'CONNAME': '127.0.0.1',
                        'RQMNAME': '',
                        'STATUS': 'RUNNING',
                        'SUBSTATE': 'RECEIVE',
                        'XMITQ': ''
                        }
        mq_manager = 'TEST'
        metric_type = 'connection_count'
        conn_count = 2
        check_data = 'mq_channel_connection_count{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", rqmname="", channel="ADMIN.SVRCONN"} 2\n'
        self.assertEqual(check_data, make_metric_for_mq_channels_status(channel_data, mq_manager, metric_type, conn_count))

    def test_make_metric_status(self):
        status_dict = {
                     'STARTING': 2,
                     'RUNNING': 3,
                     'STOPPED': 6,
                     '': 0,
                     }
        for status in status_dict:
            status_name = status
            status_code = status_dict[status]
            channel_data = {'CHANNEL': 'ADMIN.SVRCONN',
                            'CHLTYPE': 'SVRCONN',
                            'CONNAME': '127.0.0.1',
                            'RQMNAME': '',
                            'STATUS': status_name,
                            'SUBSTATE': 'RECEIVE',
                            'XMITQ': ''
                            }
            mq_manager = 'TEST'
            metric_type = 'status'
            check_data = 'mq_channel_status{qmname="TEST", conname="127.0.0.1", substate="RECEIVE", xmitq="", chltype="SVRCONN", rqmname="", channel="ADMIN.SVRCONN"} %s\n' % (status_code)
            self.assertEqual(check_data, make_metric_for_mq_channels_status(channel_data, mq_manager, metric_type))


if __name__ == '__main__':
    unittest.main()
