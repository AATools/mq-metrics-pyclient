# -*- coding: utf-8 -*-
"""Tests for `mq_metrics_client`."""
import os
import sys
import unittest
import argparse
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from mq_metrics_client import (
    get_mq_metrics,
    put_metric_to_gateway,
    static_content,
    parse_commandline_args,
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
    def mock_put_metric_to_gateway(metric_data, job, pushgateway_host, pushgateway_port):
        """Mock for `put_metric_to_gateway` function."""
        pass


class TestGetMQMetrics(unittest.TestCase):
    pushgateway_host = 'testhost'
    pushgateway_port = '9091'

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
    def test_get_mq_metrics(self,
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
        """Tests for `get_mq_metrics` function."""
        with patch('mq_metrics_client.get_mq_manager_metrics') as mock_get_mq_manager_metrics:
            mock_get_mq_manager_metrics.return_value = 'MQ manager is ok', 1
            self.assertEqual(
                get_mq_metrics(
                    pushgateway_host=self.pushgateway_host,
                    pushgateway_port=self.pushgateway_port),
                None)
            mock_get_mq_manager_metrics.return_value = 'MQ manager is ok', 0
            self.assertEqual(
                get_mq_metrics(
                    pushgateway_host=self.pushgateway_host,
                    pushgateway_port=self.pushgateway_port),
                None)

    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    @patch('mq_metrics_client.logger.error', side_effect=Exception())
    def test_get_mq_metrics_exception(self, mock_logging_info, mock_logging_error):
        """Test for `get_mq_metrics` function for exceptions."""
        with patch('mq_metrics_client.run_mq_command') as mock_mq_command:
            mock_mq_command.side_effect = PrometheusBadResponse
            self.assertRaises(
                Exception,
                get_mq_metrics,
                pushgateway_host=self.pushgateway_host,
                pushgateway_port=self.pushgateway_port)
            mock_mq_command.side_effect = Exception()
            self.assertRaises(
                Exception,
                get_mq_metrics,
                pushgateway_host=self.pushgateway_host,
                pushgateway_port=self.pushgateway_port)


class TestPutMetricToGateway(unittest.TestCase):
    metric_data=''
    job='TEST'
    pushgateway_host = 'testhost'
    pushgateway_port = '9091'

    Mocked = MockFunction()
    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    def test_put_metric_to_gateway(self, mock_logging_info):
        """Tests for `put_metric_to_gateway` function."""
        with patch('mq_metrics_client.requests.put') as mock_request:
            mock_request.return_value.ok = True
            self.assertEqual(
                put_metric_to_gateway(
                    metric_data=self.metric_data,
                    job=self.job,
                    pushgateway_host=self.pushgateway_host,
                    pushgateway_port=self.pushgateway_port),
                None)
            mock_request.return_value.ok = False
            self.assertRaises(
                PrometheusBadResponse,
                put_metric_to_gateway,
                metric_data=self.metric_data,
                job=self.job,
                pushgateway_host=self.pushgateway_host,
                pushgateway_port=self.pushgateway_port)

    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    def test_put_metric_to_gateway_except(self,  mock_logging_info):
        """Test for `put_metric_to_gateway` function for `ConnectionError` exceptions."""
        self.assertRaises(
            PrometheusBadResponse,
            put_metric_to_gateway,
            metric_data=self.metric_data,
            job=self.job,
            pushgateway_host=self.pushgateway_host,
            pushgateway_port=self.pushgateway_port)


class TestStaticContent(unittest.TestCase):
    def test_static_content(self):
        """Test for `static_content` function."""
        self.assertIsInstance(static_content(), str)


class TestParseCommandlineArgs(unittest.TestCase):
    pushgateway_host = 'testhost'
    pushgateway_port = '9091'

    Mocked = MockFunction()
    @patch('mq_metrics_client.logger.info', side_effect=Mocked.mock_logging_info)
    @patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            pushgateway_host= pushgateway_host,
            pushgateway_port= pushgateway_port))
    def test_parse_commandline_args(self, mock_logging_info, mock_args):
        """Test for `parse_commandline_args` function."""
        self.assertEqual(
            parse_commandline_args(), 
            (self.pushgateway_host, self.pushgateway_port))


if __name__ == '__main__':
    unittest.main()
