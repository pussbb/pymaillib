# -*- coding: utf-8 -*-
"""
    Imap4 NAMESPACE Command
    ~~~~~~~~~~~~~~~~
    Executes IMAP NAMESPACE command

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from .._parsers import ResponseTokenizer
from . import ImapBaseCommand
from ..entity.server import Namespaces


class Namespace(ImapBaseCommand):
    """
    
    """

    _COMMAND = 'NAMESPACE'

    def error_message(self):
        """Default error message for unsuccessful NAMESPACE command

        :return: str
        """
        return 'Could not determine namespaces.'

    def run(self, imap_obj: imaplib.IMAP4):
        """Sends IMAP NAMESPACE command.

        Raises: ImapRuntimeError - if command executions failed

        :param imap_obj: imaplib.IMAP4
        :return: Namespaces
        """
        typ, data = imap_obj.namespace()
        self.check_response(typ, data)
        return Namespaces.parse(list(ResponseTokenizer(data[0], [])))
