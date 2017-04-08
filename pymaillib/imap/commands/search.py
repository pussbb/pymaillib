# -*- coding: utf-8 -*-
"""
    Imap4 Store Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP SEARCH cammand

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from ..query.builders.search import SearchQueryBuilder
from . import ImapBaseCommand
from ..exceptions import ImapInvalidArgument


class ImapSearchCommand(ImapBaseCommand):
    """Executes  IMAP SEARCH cammand

    """

    _COMMAND = 'SEARCH'

    def __init__(self, query: SearchQueryBuilder, charset=None):
        """Creates instance of SEARCH IMAP command

        Raises:
            ImapRuntimeError - if :param query is not instance of
                                SearchQueryBuilder

        :param query: FetchQueryBuilder
        :param charset: Any
        :return:
        """
        if not isinstance(query, SearchQueryBuilder):
            raise ImapInvalidArgument('query', query)
        self.__search_query = query
        self.__charset = charset

    def run(self, imap_obj: imaplib.IMAP4):
        """Executes IMAP SEARCH command according to the requested
         SearchQueryBuilder.

        :param imap_obj:
        """
        typ, data = imap_obj.search(self.__charset, str(self.__search_query))
        self.check_response(typ, data)
        if not data:
            return []
        for uid in data[0].split(b' '):
            yield int(uid)
