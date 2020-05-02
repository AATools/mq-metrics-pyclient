# -*- coding: utf-8 -*-
import os
import sys
import unittest
from modules.mq_manager import (
    format_output,
    make_metric_for_mq_manager_status,
    get_mq_manager_status,
    get_mq_managers,
    get_metric_name,
    get_metric_annotation)
sys.path.append(os.getcwd())


class TestFormatOutput(unittest.TestCase):
    def test_format_output_running(self):
        input_data = ['QMNAME(TEST',
                      ' STATUS(Running',
                      ' DEFAULT(yes',
                      ' STANDBY(Not permitted',
                      ' INSTNAME(Installation1',
                      ' INSTPATH(/opt/mqm',
                      ' INSTVER(7.5.0.1',
                      '\n']
        check_data = {'DEFAULT': 'yes',
                      'INSTNAME': 'Installation1',
                      'INSTPATH': '/opt/mqm',
                      'INSTVER': '7.5.0.1',
                      'QMNAME': 'TEST',
                      'STANDBY': 'Not permitted',
                      'STATUS': 1}
        self.assertEqual(
            check_data,
            format_output(input_data))

    def test_format_output_stopped(self):
        input_data = ['QMNAME(TEST',
                      ' STATUS(Stopped',
                      ' DEFAULT(yes',
                      ' STANDBY(Not permitted',
                      ' INSTNAME(Installation1',
                      ' INSTPATH(/opt/mqm',
                      ' INSTVER(7.5.0.1',
                      '\n']
        check_data = {'DEFAULT': 'yes',
                      'INSTNAME': 'Installation1',
                      'INSTPATH': '/opt/mqm',
                      'INSTVER': '7.5.0.1',
                      'QMNAME': 'TEST',
                      'STANDBY': 'Not permitted',
                      'STATUS': 0}
        self.assertEqual(
            check_data,
            format_output(input_data))


class TestGetMqManagerStatus(unittest.TestCase):
    def test_get_mq_manager_status(self):
        input_data = '''\
QMNAME(TEST)  STATUS(Running) \
DEFAULT(yes) STANDBY(Not permitted) \
INSTNAME(Installation1) INSTPATH(/opt/mqm) \
INSTVER(7.5.0.1)\n'''
        check_data = {'DEFAULT': 'yes',
                      'INSTNAME': 'Installation1',
                      'INSTPATH': '/opt/mqm',
                      'INSTVER': '7.5.0.1',
                      'QMNAME': 'TEST',
                      'STANDBY': 'Not permitted',
                      'STATUS': 1}
        self.assertEqual(
            check_data,
            get_mq_manager_status(input_data))


class TestGetMqManagers(unittest.TestCase):
    def test_get_mq_managers(self):
        input_data = 'QMNAME(TEST) STATUS(Running)\n'
        check_data = ['TEST']
        self.assertEqual(
            check_data,
            get_mq_managers(input_data))


class TestMakeMetricForMqManagerStatus(unittest.TestCase):
    def test_make_metric_for_mq_manager_status(self):
        input_data = {'DEFAULT': 'yes',
                      'INSTNAME': 'Installation1',
                      'INSTPATH': '/opt/mqm',
                      'INSTVER': '7.5.0.1',
                      'QMNAME': 'TEST',
                      'STANDBY': 'Not permitted',
                      'STATUS': 1}
        check_data = ('''\
mq_manager_status{default="yes", instname="Installation1", \
instpath="/opt/mqm", instver="7.5.0.1", qmname="TEST", \
standby="Not permitted"} 1\n''', 1)
        self.assertEqual(
            check_data,
            make_metric_for_mq_manager_status(input_data))


class GetMetricAnnotation(unittest.TestCase):
    def test_get_metric_name(self):
        self.assertEqual('mq_manager_status', get_metric_name('status'))

    def test_get_metric_annotation(self):
        self.assertIsInstance(get_metric_annotation(), dict)
        self.assertIsInstance(get_metric_annotation().get('status'), str)


if __name__ == '__main__':
    unittest.main()
