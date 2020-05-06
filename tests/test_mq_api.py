# -*- coding: utf-8 -*-
"""Tests for `mq_api`."""
import os
import sys
import unittest
from modules.mq_api import (
    check_not_empty_list,
    add_annotation)
sys.path.append(os.getcwd())


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
