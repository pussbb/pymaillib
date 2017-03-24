# -*- coding: utf-8 -*-
"""
    Imap4 Fetch Query Builder
    ~~~~~~~~~~~~~~~~
    Imap4 helper human readable library  to construct valid imap fetch
    request string

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from .utils import is_iterable
from .exceptions import ImapRuntimeError
from .entity.fetch_item import FetchItem, FETCH_ITEMS


class FetchQueryBuilder(object):
    """Builds valid string for IMAP FETCH command

    """

    def __init__(self, seq_ids=None, uids=None):
        self.__items = set()
        self.fetch_uid()
        if seq_ids and uids:
            raise ImapRuntimeError('You can specify only sequence or uid '
                                   '(range). But not both.')
        if not seq_ids and not uids:
            raise ImapRuntimeError('Please specify sequence or uid range')

        self.__uids = uids
        self.__seq = seq_ids

    def add(self, *args):
        """Add some data items for IMAP FETCH command

        :param args:
        :return:
        """
        for arg in args:
            self.__items.add(str(arg))

    @property
    def uids(self):
        """List of UID's to fetch from server

        :return:
        """
        return self.__uids

    @property
    def sequence(self):
        """List of sequence numbers to fetch from the server

        :return:
        """
        return self.__seq

    def build(self):
        """Builds valid query string for IMAP FETCH command

        :return: tuple
        """
        return self.__build_range(), '({})'.format(' '.join(self.__items))

    def __build_range(self):
        keys = self.uids
        if not keys:
            keys = self.sequence
        if not is_iterable(keys):
            keys = [keys]
        return ','.join(keys)

    def __repr__(self):
        return ' '.join(self.build())

    def _get_fetch_item(self, name: bytes):
        """Get item from list with available items to fetch it want raise
        exception for now if name was not found it take base class FetchItem

        :param name:
        :return:
        """
        return FETCH_ITEMS.get(name, FetchItem)()

    def fetch_body(self, part=None, size=0):
        """Add to a fetch command BODY ATOM

        :param part: part according RFC
        :param size: length of requested part or body
        """
        body_part = self._get_fetch_item(b'BODY')
        body_part.size = size
        body_part.part = part
        self.add(body_part)

    def fetch_body_peek(self, part=None, size=0):
        """Add to a fetch command BODY.PEEK ATOM

        :param part: part according RFC
        :param size: length of requested part or body
        """
        body_part = self._get_fetch_item(b'BODY.PEEK')
        body_part.size = size
        body_part.part = part
        self.add(body_part)

    def fetch_envelope(self):
        """Add ENVELOPE message item to fetch query command

        """
        self.add(self._get_fetch_item(b'ENVELOPE'))

    def fetch_body_structure(self):
        """Add BODYSTRUCTURE message item to fetch query command

        """
        self.add(self._get_fetch_item(b'BODYSTRUCTURE'))

    def fetch_uid(self):
        """Add UID message item to fetch query command

        """
        self.add(self._get_fetch_item(b'UID'))

    def fetch_flags(self):
        """Add FLAGS message item to fetch query command

        """
        self.add(self._get_fetch_item(b'FLAGS'))

    def fetch_internal_date(self):
        """Add INTERNALDATE message item to fetch query command

        """
        self.add(self._get_fetch_item(b'INTERNALDATE'))

    def fetch_rfc822(self):
        """Add RFC822 item to fetch query command

        """
        self.add(self._get_fetch_item(b'RFC822'))

    def fetch_rfc822_header(self):
        """Add RFC822.HEADER item to fetch query command

        """
        self.add(self._get_fetch_item(b'RFC822.HEADER'))

    def fetch_rfc822_size(self):
        """Add RFC822.SIZE item to fetch query command

        """
        self.add(self._get_fetch_item(b'RFC822.SIZE'))

    def fetch_rfc822_text(self):
        """Add RFC822.TEXT item to fetch query command

        """
        self.add(self._get_fetch_item(b'RFC822.TEXT'))

    @staticmethod
    def all(sequence=None, uids=None):
        """ALL
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE ENVELOPE)

        :return: FetchQueryBuilder object
        """
        query = FetchQueryBuilder(sequence, uids)
        query.fetch_flags()
        query.fetch_rfc822_size()
        query.fetch_internal_date()
        query.fetch_envelope()
        return query

    @staticmethod
    def fast(sequence=None, uids=None):
        """ FAST
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE)

        :return: FetchQueryBuilder object
        """
        query = FetchQueryBuilder(sequence, uids)
        query.fetch_flags()
        query.fetch_rfc822_size()
        query.fetch_internal_date()
        return query

    @staticmethod
    def full(sequence=None, uids=None):
        """FULL
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE ENVELOPE BODY)

        :return: FetchQueryBuilder object
        """
        query = FetchQueryBuilder.all(sequence, uids)
        query.fetch_body()
        return query


