# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import unittest
from datetime import datetime

from pymaillib.imap.query.builders.search import SearchQueryBuilder


class SearchQueryBuilderTest(unittest.TestCase):

    def test_simple(self):
        search = SearchQueryBuilder(uids=1)
        search.seen().recent().bcc('ss"ss').since(datetime.now())
        self.__test('RECENT SEEN UID 1 BCC "ss\"ss" SINCE 07-Apr-2017',
                          str(search))

    def test_seq_set(self):
        search = SearchQueryBuilder(1)
        search.seen().recent().bcc('ss"ss').since(datetime.now())
        self.__test('1 RECENT SEEN BCC "ss\"ss" SINCE 07-Apr-2017',
                    str(search))

    def __test(self, original, generated):
        items = generated.split(' ')
        for item in original.split(' '):
            if not item:
                continue
            self.assertIn(item, items)

        items = original.split(' ')
        for item in generated.split(' '):
            if not item:
                continue
            self.assertIn(item, items)
