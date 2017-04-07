# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import unittest

from pymaillib.imap.exceptions import ImapRuntimeError
from pymaillib.imap.query.builders.store import StoreQueryBuilder


class StoreQueryBuilderTest(unittest.TestCase):

    def test_simple(self):
        with self.assertRaises(ImapRuntimeError):
            str(StoreQueryBuilder(1))

    def test_replace(self):
        query = StoreQueryBuilder(1)
        query.replace(r'\SEEN')
        self.assertEquals(r'1 FLAGS (\SEEN)', str(query))
        query.silent = True
        self.assertEquals(r'1 FLAGS.SILENT (\SEEN)', str(query))

    def test_add(self):
        query = StoreQueryBuilder(1)
        query.add(r'\SEEN')
        self.assertEquals(r'1 +FLAGS (\SEEN)', str(query))
        query.silent = True
        self.assertEquals(r'1 +FLAGS.SILENT (\SEEN)', str(query))

    def test_remove(self):
        query = StoreQueryBuilder(1)
        query.remove(r'\SEEN')
        self.assertEquals(r'1 -FLAGS (\SEEN)', str(query))
        query.silent = True
        self.assertEquals(r'1 -FLAGS.SILENT (\SEEN)', str(query))

