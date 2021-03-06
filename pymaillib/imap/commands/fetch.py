# -*- coding: utf-8 -*-
"""
    Imap4 Fetch Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP Fetch cammand

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from ..query.builders.fetch import FetchQueryBuilder
from . import ImapBaseCommand
from ..entity.email_message import ImapFetchedItem
from ..exceptions import ImapInvalidArgument
from ..parsers import tokenize_atom_response
from ..utils import build_imap_response_line


class ImapFetchCommand(ImapBaseCommand):
    """Executes  IMAP Fetch cammand

    """

    _COMMAND = 'FETCH'

    def __init__(self, query: FetchQueryBuilder):
        """Creates instance of Fetch IMAP command

        Raises:
            ImapRuntimeError - if :param query is not instance of
                                FetchQueryBuilder

        :param query: FetchQueryBuilder
        :return:
        """
        if not isinstance(query, FetchQueryBuilder):
            raise ImapInvalidArgument('query', query)
        self.__fetch_query = query

    def run(self, imap_obj: imaplib.IMAP4):
        """Executes IMAP fetch command according to the requested
         FetchQueryBuilder.

        :param imap_obj:
        """
        func = 'fetch'
        args = self.__fetch_query.build()
        if self.__fetch_query.uids:
            func = 'uid'
            args = ('fetch',) + args

        typ, data = getattr(imap_obj, func)(*args)
        self.check_response(typ, data)
        for line, literals in build_imap_response_line(data):
            yield ImapFetchedItem(tokenize_atom_response(line, literals))
