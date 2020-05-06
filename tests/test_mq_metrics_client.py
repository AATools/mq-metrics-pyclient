# -*- coding: utf-8 -*-
"""Tests for `mq_metrics_client`."""
import os
import sys
import unittest
from mq_metrics_client import static_content
sys.path.append(os.getcwd())


class TestStaticContent(unittest.TestCase):
    def test_static_content(self):
        """Test for `static_content` function."""
        self.assertIsInstance(static_content(), str)


if __name__ == '__main__':
    unittest.main()
