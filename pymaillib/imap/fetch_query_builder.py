# -*- coding: utf-8 -*-
"""
    Imap4 Fetch Query Builder
    ~~~~~~~~~~~~~~~~
    Imap4 helper human readable library  to construct valid imap fetch
    request string

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from typing import Any, List, Tuple

from .utils import is_iterable
from .exceptions import ImapRuntimeError
from .entity.fetch_item import FetchItem, FETCH_ITEMS


def build_numeric_sequence(data: List[int]) -> List[str]:
    """Builds range from list of integers if it possible.
    for e.g. ::
        >>> res = build_numeric_sequence([0, 1, 2, 3, 4, 5, 6, 56, 44, 45, 46])
        >>> print(res)
        ['1:6', '44:46', '56']
        >>>
        
    :param data: list of integers
    :return: list of parsed list
    """
    prev = -1
    start = None
    res = []
    for item in filter(None, sorted(set(data))):
        if prev+1 == item:
            if not start:
                start = prev
                if res and res[-1] == prev:
                    res.pop()
        else:
            if start:
                res.append('{}:{}'.format(start, prev))
                start = None
            res.append(item)
        prev = item
    if start:
        res.append('{}:{}'.format(start, prev))
    return [str(item) for item in res]


def build_sequence(data: Any):
    """Builds sequence for fetch command.
    for e.g.::
        >>>res = build_sequence('1:*')
        >>>print(res)
        1:*
        >>>
        >>>res = build_sequence('1,2,3,4,5,6,7,47,8,87,5:88')
        >>>print(res)
        5:88,1:8,47,87
        >>>
        >>>res = build_sequence([0, 1, 2, 3, 4, 5, 6, 56, 44, 45, 46])
        >>>print(res)
        1:6,44:46,56
        >>>
    
    :param data: Any
    :return: string
    """
    if isinstance(data, (bytearray, bytes)):
        data = data.decode()
    if isinstance(data, str):
        data = data.split(',')
    literals = []
    numeric = []
    for item in data:
        if str(item).isdigit():
            numeric.append(int(item))
            continue
        if ':' in item:
            literals.append(item)
        else:
            raise Exception(item)
    return ','.join(literals + build_numeric_sequence(numeric))


class FetchQueryBuilder(object):
    """Builds valid string for IMAP FETCH command

    """

    def __init__(self, seq_ids=None, uids=None):
        self.__items = set()
        self.fetch_uid()
        if seq_ids and uids:
            raise ImapRuntimeError('You can specify only sequence or uid '
                                   '(range).')
        if not seq_ids and not uids:
            raise ImapRuntimeError('Please specify sequence or uid range.'
                                   ' But not both.')

        self.__uids = uids
        self.__seq = seq_ids
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

    @property
    def uids(self) -> Any:
        """List of UID's to fetch from server

        :return: Any
        """
        return self.__uids

    @property
    def sequence(self) -> Any:
        """List of sequence numbers to fetch from the server

        :return: Any
        """
        return self.__seq

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
        return self.__build_range(), '({})'.format(
            ' '.join(list(self.__items) + [header_items])
        )

    def __build_range(self) -> str:
        """Helper function to build range of fetch items.  
        
        :return: string
        """
        return build_sequence(filter(None, (self.uids, self.sequence)))

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
        
        :param body_part: 
        :return: FetchQueryBuilder obj
        """
        return self.fetch_body('HEADER')

    def fetch_header_item(self, item:str) -> 'FetchQueryBuilder':
        """fetch header item
        
        :param item: header item name 
        :return: FetchQueryBuilder
        """
        self.__header_items.add(item)
        return self

    def __body_item(self, peek: bool, part: str=None, size: int = 0) \
            -> FetchItem:
        """
        
        :param peek: use PEEK 
        :param part: part according RFC
        :param size: length of part or body
        :return: FetchItem
        """
        if peek:
            body_part = self._get_fetch_item(b'BODY.PEEK')
        else:
            body_part = self._get_fetch_item(b'BODY')
        body_part.size = size
        body_part.part = part
        return body_part

    def fetch_body(self, part=None, size=0) -> 'FetchQueryBuilder':
        """Add to a fetch command BODY ATOM

        :param part: part according RFC
        :param size: length of part or body
        :return: FetchQueryBuilder obj
        """
        self.add(self.__body_item(self.__peek, part, size))
        return self

    def fetch_body_peek(self, part=None, size=0) -> 'FetchQueryBuilder':
        """Add to a fetch command BODY.PEEK ATOM

        :param part: part according RFC
        :param size: length of part or body
        :return: FetchQueryBuilder obj
        """
        self.add(self.__body_item(True, part, size))
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
        return FetchQueryBuilder(sequence, uids)\
            .fetch_flags()\
            .fetch_rfc822_size()\
            .fetch_internal_date()\
            .fetch_envelope()

    @staticmethod
    def fast(sequence=None, uids=None) -> 'FetchQueryBuilder':
        """ FAST
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE)

        :return: FetchQueryBuilder object
        """
        return FetchQueryBuilder(sequence, uids)\
            .fetch_flags()\
            .fetch_rfc822_size()\
            .fetch_internal_date()

    @staticmethod
    def full(sequence=None, uids=None) -> 'FetchQueryBuilder':
        """FULL
         Macro equivalent to: (FLAGS INTERNALDATE RFC822.SIZE ENVELOPE BODY)

        :return: FetchQueryBuilder object
        """
        return FetchQueryBuilder.all(sequence, uids).fetch_body()


