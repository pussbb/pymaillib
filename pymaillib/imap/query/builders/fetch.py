# -*- coding: utf-8 -*-
"""
    Imap4 Fetch Query Builder
    ~~~~~~~~~~~~~~~~
    Imap4 helper human readable library  to construct valid imap fetch
    request string

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from typing import Tuple

from . import BaseQueryBuilder
from ...entity.fetch_item import FetchItem, FETCH_ITEMS


class FetchQueryBuilder(BaseQueryBuilder):
    """Builds valid string for IMAP FETCH command

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__items = set()
        self.fetch_uid()
        self.__peek = False
        self.__header_items = set()

    def add(self, *args) -> 'FetchQueryBuilder':
        """Add some data items for IMAP FETCH command

        :param args:
        :return: FetchQueryBuilder obj
        """
        for arg in args:
            self.__items.add(str(arg))
        return self

    def set_peek(self, value: bool) -> 'FetchQueryBuilder':
        """Set using PEEK for fetching some data.

        :param value:
        :return: FetchQueryBuilder obj
        """
        self.__peek = value
        return self

    def build(self) -> Tuple[str, str]:
        """Builds valid query string for IMAP FETCH command

        :return: tuple(items range, data to fetch)
        """
        header_items = ""
        if self.__header_items:
            items = 'HEADER.FIELDS ({})'.format(
                ' '.join(self.__header_items)
            )
            header_items = str(self.__body_item(self.__peek, items, 0))
        return self._build_range(), '({})'.format(
            ' '.join(list(self.__items) + [header_items])
        )

    def __repr__(self) -> str:
        return ' '.join(self.build())

    def _get_fetch_item(self, name: bytes):
        """Get item from list with available items to fetch it want raise
        exception for now if name was not found it take base class FetchItem

        :param name:
        :return: FetchQueryBuilder obj
        """
        return FETCH_ITEMS.get(name, FetchItem)()

    def fetch_header(self) -> 'FetchQueryBuilder':
        """Alias to fetch_rfc822_header

        :return: FetchQueryBuilder obj
        """
        return self.fetch_body('HEADER')

    def fetch_header_item(self, item: str) -> 'FetchQueryBuilder':
        """fetch header item

        :param item: header item name
        :return: FetchQueryBuilder
        """
        self.__header_items.add(item)
        return self

    def __body_item(self, peek: bool, part: str = '', size: int = 0,
                    start_from: int = 0) -> FetchItem:
        """Create BODY section

        :param peek: use PEEK
        :param part: part according RFC
        :param size: length of part or body
        :param start_from: starting position of first octets to fetch
        :return: FetchItem
        """

        if peek:
            body_part = self._get_fetch_item(b'BODY.PEEK')
        else:
            body_part = self._get_fetch_item(b'BODY')
        body_part.size = size
        body_part.start_from = start_from
        body_part.part = part
        return body_part

    def fetch_body(self, part: str = None, size: int = 0, start_from: int = 0) \
            -> 'FetchQueryBuilder':
        """Add to a fetch command BODY ATOM

        :param part: part according RFC
        :param size: length of part or body
        :param start_from: starting position of first octets to fetch
        :return: FetchQueryBuilder obj
        """
        self.add(self.__body_item(self.__peek, part, size, start_from))
        return self

    def fetch_body_peek(self, part: str = '', size: int = 0,
                        start_from: int = 0) \
            -> 'FetchQueryBuilder':
        """Add to a fetch command BODY.PEEK ATOM

        :param part: part according RFC
        :param size: length of part or body
        :param start_from: starting position of first octets to fetch
        :return: FetchQueryBuilder obj
        """
        self.add(self.__body_item(True, part, size, start_from))
        return self

    def fetch_envelope(self) -> 'FetchQueryBuilder':
        """Add ENVELOPE message item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'ENVELOPE'))
        return self

    def fetch_body_structure(self) -> 'FetchQueryBuilder':
        """Add BODYSTRUCTURE message item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'BODYSTRUCTURE'))
        return self

    def fetch_uid(self) -> 'FetchQueryBuilder':
        """Add UID message item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'UID'))
        return self

    def fetch_flags(self) -> 'FetchQueryBuilder':
        """Add FLAGS message item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'FLAGS'))
        return self

    def fetch_internal_date(self) -> 'FetchQueryBuilder':
        """Add INTERNALDATE message item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'INTERNALDATE'))
        return self

    def fetch_rfc822(self) -> 'FetchQueryBuilder':
        """Add RFC822 item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'RFC822'))
        return self

    def fetch_rfc822_header(self) -> 'FetchQueryBuilder':
        """Add RFC822.HEADER item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'RFC822.HEADER'))
        return self

    def fetch_rfc822_size(self) -> 'FetchQueryBuilder':
        """Add RFC822.SIZE item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'RFC822.SIZE'))
        return self

    def fetch_rfc822_text(self) -> 'FetchQueryBuilder':
        """Add RFC822.TEXT item to fetch query command

        :return: FetchQueryBuilder obj
        """
        self.add(self._get_fetch_item(b'RFC822.TEXT'))
        return self

    @staticmethod
    def all(sequence=None, uids=None) -> 'FetchQueryBuilder':
        """ALL
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE ENVELOPE)

        :return: FetchQueryBuilder object
        """
        return FetchQueryBuilder(sequence, uids) \
            .fetch_flags() \
            .fetch_rfc822_size() \
            .fetch_internal_date() \
            .fetch_envelope()

    @staticmethod
    def fast(sequence=None, uids=None) -> 'FetchQueryBuilder':
        """ FAST
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE)

        :return: FetchQueryBuilder object
        """
        return FetchQueryBuilder(sequence, uids) \
            .fetch_flags() \
            .fetch_rfc822_size() \
            .fetch_internal_date()

    @staticmethod
    def full(sequence=None, uids=None) -> 'FetchQueryBuilder':
        """FULL
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE ENVELOPE BODY)

        :return: FetchQueryBuilder object
        """
        return FetchQueryBuilder.all(sequence, uids).fetch_body()
