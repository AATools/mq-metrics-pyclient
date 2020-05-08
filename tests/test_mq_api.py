# -*- coding: utf-8 -*-
"""Tests for `mq_api`."""
import os
import sys
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from modules.mq_api import (
    run_mq_command,
    check_not_empty_list,
    add_annotation)
sys.path.append(os.getcwd())


def mock_execute_command(command):
    """Mock for `execute_command` function."""
    return command


class TestRunMqCommand(unittest.TestCase):
    @patch('modules.mq_api.execute_command', side_effect=mock_execute_command)
    def test_run_mq_command(self, execute_command):
        """Tests for `run_mq_command` function."""
        self.assertEqual(
            run_mq_command(task='get_mq_managers'),
            'dspmq')
        self.assertEqual(
            run_mq_command(task='get_mq_manager_status', mqm='TEST'),
            'dspmq -m TEST -o all')
        self.assertEqual(
            run_mq_command(
                task='get_listener',
                mqm='TEST',
                listener='LISTENER'),
            'echo "display listener(LISTENER)"| runmqsc TEST')


class TestListFunctions(unittest.TestCase):
    def test_check_not_empty_list(self):
        """Tests for `check_not_empty_list` function."""
        self.assertEqual(check_not_empty_list(lis1=list()), 0)
        self.assertEqual(check_not_empty_list(lis1=['test']), 1)

    def test_add_annotation(self):
        """Tests for `add_annotation` function."""
        self.assertEqual(add_annotation(lis1=list(), annotation='test'), [])
        self.assertEqual(add_annotation(lis1=['test'], annotation='Good'), ['Good', 'test'])


if __name__ == '__main__':
    unittest.main()
