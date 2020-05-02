# -*- coding: utf-8 -*-
import os
import sys
import unittest
from modules.mq_api import (
    check_not_empty_list,
    add_annotation)
sys.path.append(os.getcwd())


class TestListFunctions(unittest.TestCase):
    def test_check_not_empty_list(self):
        self.assertEqual(check_not_empty_list([]), 0)
        self.assertEqual(check_not_empty_list(['test']), 1)

    def test_add_annotation(self):
        self.assertEqual(add_annotation([], 'test'), [])
        self.assertEqual(add_annotation(['test'], 'Good'), ['Good', 'test'])


if __name__ == '__main__':
    unittest.main()
