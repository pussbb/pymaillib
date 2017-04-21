# -*- coding: utf-8 -*-
"""
    Imap4 Query Builders
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from typing import List, Any

from ...exceptions import ImapRuntimeError


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
        if prev + 1 == item:
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
    for item in filter(None, data):
        if str(item).isdigit():
            numeric.append(int(item))
            continue
        if ':' in item:
            literals.append(item)
        elif isinstance(item, (tuple, set, list)):
            return build_sequence(item)
        else:
            raise Exception(item)
    return ','.join(literals + build_numeric_sequence(numeric))


class BaseQueryBuilder(object):
    def __init__(self, seq_ids=None, uids=None, requires_msg_set=True):
        if seq_ids and uids:
            raise ImapRuntimeError('You can specify only sequence or uid '
                                   '(range). But not both.')
        if (not seq_ids and not uids) and requires_msg_set:
            raise ImapRuntimeError('Please specify sequence or uid range.')
        self.__uids = uids
        self.__seq = seq_ids

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

    def _build_range(self) -> str:
        """Helper function to build range of fetch items.

        :return: string
        """
        return build_sequence(filter(None, (self.uids, self.sequence)))
