# -*- coding: utf-8 -*-
"""Tests for `mq_metrics_client`."""
import os
import sys
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from mq_metrics_client import (
    main,
    put_metric_to_gateway,
    static_content,
    PrometheusBadResponse)
sys.path.append(os.getcwd())


class MockFunction():
    @staticmethod
    def mock_logging_info(msg):
        """Mock for `logger.info` function."""
        pass

    @staticmethod
    def mock_run_mq_command(**kwargs):
        """Mock for `run_mq_command` function."""
        return 'OK'

    @staticmethod
    def mock_get_mq_managers(mq_managers_data):
        """Mock for `get_mq_managers` function."""
        return ['TEST']

    @staticmethod
    def mock_get_listeners(listeners_data):
        """Mock for `get_listeners` function."""
        return ['TEST']

    @staticmethod
    def mock_get_mq_listeners_metrics(listeners, mq_manager):
        """Mock for `get_mq_listeners_metrics` function."""
        return 'MQ listener is ok'

    @staticmethod
    def mock_channels_status(mqm):
        """Mock for `channels_status` function."""
        return ['TEST']

    @staticmethod
    def mock_get_mq_channels_metrics(mq_channels, mq_manager):
        """Mock for `get_mq_channels_metrics` function."""
        return 'MQ channel is ok'

    @staticmethod
    def mock_get_queues_metrics(mq_manager):
        """Mock for `get_queues_metrics` function."""
        return 'MQ queue is ok'

    @staticmethod
    def mock_get_queues_metrics_monitor(mq_manager):
        """Mock for `get_queues_metrics_monitor` function."""
        return 'MQ queue is ok'

    @staticmethod
    def mock_put_metric_to_gateway(metric_data, job):
        """Mock for `put_metric_to_gateway` function."""
        pass


class TestMain(unittest.TestCase):
    Mocked = MockFunction()
    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    @patch('mq_metrics_client.run_mq_command', side_effect=Mocked.mock_run_mq_command)
    @patch('mq_metrics_client.get_mq_managers', side_effect=Mocked.mock_get_mq_managers)
    @patch('mq_metrics_client.get_listeners', side_effect=Mocked.mock_get_listeners)
    @patch('mq_metrics_client.get_mq_listeners_metrics', side_effect=Mocked.mock_get_mq_listeners_metrics)
    @patch('mq_metrics_client.channels_status', side_effect=Mocked.mock_channels_status)
    @patch('mq_metrics_client.get_mq_channels_metrics', side_effect=Mocked.mock_get_mq_channels_metrics)
    @patch('mq_metrics_client.get_queues_metrics', side_effect=Mocked.mock_get_queues_metrics)
    @patch('mq_metrics_client.get_queues_metrics_monitor', side_effect=Mocked.mock_get_queues_metrics_monitor)
    @patch('mq_metrics_client.put_metric_to_gateway', side_effect=Mocked.mock_put_metric_to_gateway)
    def test_main(self,
                  mock_logging_info,
                  mock_run_mq_command,
                  mock_get_mq_managers,
                  mock_get_listeners,
                  mock_get_mq_listeners_metrics,
                  mock_channels_status,
                  mock_get_mq_channels_metrics,
                  mock_get_queues_metrics,
                  mock_get_queues_metrics_monitor,
                  mock_put_metric_to_gateway):
        """Tests for `main` function."""
        with patch('mq_metrics_client.get_mq_manager_metrics') as mock_get_mq_manager_metrics:
            mock_get_mq_manager_metrics.return_value = 'MQ manager is ok', 1
            self.assertEqual(main(), None)
            mock_get_mq_manager_metrics.return_value = 'MQ manager is ok', 0
            self.assertEqual(main(), None)

    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    @patch('mq_metrics_client.logger.error', side_effect=Exception())
    def test_main_exception(self, mock_logging_info, mock_logging_error):
        """Test for `main` function for exceptions."""
        with patch('mq_metrics_client.run_mq_command') as mock_mq_command:
            mock_mq_command.side_effect = PrometheusBadResponse
            self.assertRaises(Exception, main)
            mock_mq_command.side_effect = Exception()
            self.assertRaises(Exception, main)


class TestPutMetricToGateway(unittest.TestCase):
    Mocked = MockFunction()
    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    def test_put_metric_to_gateway(self, mock_logging_info):
        """Tests for `put_metric_to_gateway` function."""
        with patch('mq_metrics_client.requests.put') as mock_request:
            mock_request.return_value.ok = True
            self.assertEqual(put_metric_to_gateway(metric_data='', job='TEST'), None)
            mock_request.return_value.ok = False
            self.assertRaises(PrometheusBadResponse, put_metric_to_gateway, metric_data='', job='TEST')

    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    def test_put_metric_to_gateway_except(self,  mock_logging_info):
        """Test for `put_metric_to_gateway` function for `ConnectionError` exceptions."""
        self.assertRaises(PrometheusBadResponse, put_metric_to_gateway, metric_data='', job='TEST')


class TestStaticContent(unittest.TestCase):
    def test_static_content(self):
        """Test for `static_content` function."""
        self.assertIsInstance(static_content(), str)


if __name__ == '__main__':
    unittest.main()
