# -*- coding: utf-8 -*-
"""
    Imap4 Store Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP Fetch cammand

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from ..parsers import tokenize_atom_response
from ..query.builders.store import StoreQueryBuilder
from . import ImapBaseCommand
from ..exceptions import ImapInvalidArgument


class ImapStoreCommand(ImapBaseCommand):
    """Executes  IMAP STORE cammand

    """

    _COMMAND = 'STORE'

    def __init__(self, query: StoreQueryBuilder):
        """Creates instance of STORE IMAP command

        Raises:
            ImapRuntimeError - if :param query is not instance of
                                StoreQueryBuilder

        :param query: StoreQueryBuilder
        :return:
        """
        if not isinstance(query, StoreQueryBuilder):
            raise ImapInvalidArgument('query', query)
        self.__store_query = query

    def run(self, imap_obj: imaplib.IMAP4):
        """Executes IMAP store command according to the requested
         StoreQueryBuilder.

        :param imap_obj:
        """
        func = 'store'
        args = self.__store_query.build()
        if self.__store_query.uids:
            func = 'uid'
            args = ('store',) + args

        typ, data = getattr(imap_obj, func)(*args)
        self.check_response(typ, data)
        for line in data:
            yield dict(tokenize_atom_response(line, []))
