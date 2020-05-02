# -*- coding: utf-8 -*-
import os
import sys
import unittest
from mq_metrics_client import static_content
sys.path.append(os.getcwd())

class TestStaticContent(unittest.TestCase):
    def test_static_content(self):
        self.assertIsInstance(static_content(), str)

if __name__ == '__main__':
    unittest.main()
