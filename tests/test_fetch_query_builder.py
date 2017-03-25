# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import unittest

from pymaillib.imap.exceptions import ImapRuntimeError
from pymaillib.imap.fetch_query_builder import build_numeric_sequence, \
    build_sequence, FetchQueryBuilder


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

    def test_fetch_query_builder(self):

        with self.assertRaises(ImapRuntimeError) as excp:
            FetchQueryBuilder()
        self.assertIn('specify sequence or uid', str(excp.exception))

        with self.assertRaises(ImapRuntimeError) as excp:
            FetchQueryBuilder(seq_ids='', uids='')
        self.assertIn(' But not both', str(excp.exception))

        self.__check_substring(
            str(FetchQueryBuilder.all(1)),
            '1 (UID FLAGS INTERNALDATE RFC822.SIZE ENVELOPE)'
        )

        self.__check_substring(
            str(FetchQueryBuilder.fast(1)),
            '1 (UID FLAGS INTERNALDATE RFC822.SIZE)'
        )

        self.__check_substring(
            str(FetchQueryBuilder.full(1)),
            '1 (UID FLAGS INTERNALDATE RFC822.SIZE ENVELOPE BODY)'
        )

        query = FetchQueryBuilder(1).fetch_header_item('SUBJECT')

        self.__check_substring(
            str(query),
            '1 (UID BODY[HEADER.FIELDS (SUBJECT)])'
        )

        query.set_peek(True)
        self.__check_substring(
            str(query),
            '1 (UID BODY.PEEK[HEADER.FIELDS (SUBJECT)])'
        )

        self.__check_substring(
            str(FetchQueryBuilder(1)),
            '1 (UID)'
        )

    def __check_substring(self, generated: str, reference: str):
        for item in generated.split(' '):
            self.assertIn(item.strip('()'), reference)