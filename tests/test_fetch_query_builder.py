# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import unittest

from pymaillib.imap.fetch_query_builder import build_numeric_sequence, \
    build_sequence


class AtomParserTest(unittest.TestCase):

    def test_build_numeric_sequence(self):
        data = [
            ([0, 1, 2, 3, 4, 5, 6, 56, 44, 45, 46], ['1:6', '44:46', '56']),
            ([1], ['1']),
            ([1, 2, 3, 4, 5], ['1:5']),
            ([1, 3, 6, 8, 8], ['1', '3', '6', '8']),
            ([1, 2, 3, 4, 4], ['1:4']),
        ]
        for raw, res in data:
            self.assertCountEqual(build_numeric_sequence(raw), res)

    def test_build_sequence(self):
        data = [
            ('1:*', '1:*'),
            ('1,2,3,4,5,6,7,47,8,87,5:88', '5:88,1:8,47,87'),
            ([0, 1, 2, 3, 4, 5, 6, 56, 44, 45, 46], '1:6,44:46,56'),
            ([1], '1'),
        ]

        for raw, res in data:
            self.assertEqual(build_sequence(raw), res)