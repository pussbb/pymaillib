# -*- coding: utf-8 -*-
"""
    Imap4 X-SCALIX-ID Command
    ~~~~~~~~~~~~~~~~
    Executes IMAP X-SCALIX-ID command to get specific information about current
    logged in user for a scalix IMAP4 server

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from . import ImapBaseCommand
from .. import __version__, __description__


class ImaXScalixIDCommand(ImapBaseCommand):
    """Executes IMAP X-SCALIX-ID command to get specific information about
    current logged in user for a scalix IMAP4 server

    """

    _COMMAND = 'X-SCALIX-ID'

    def error_message(self):
        """Error message for X-SCALIX-ID

        :return:  str
        """
        return 'Could not determine scalix server info.'

    def run(self, imap_obj: imaplib.IMAP4):
        """Executes Executes IMAP X-SCALIX-ID.

        Raises: ImapRuntimeError - if command executions failed

        :param imap_obj: imaplib.IMAP4
        :return: dict
        """
        arg = '("name" "{}" "version" "{}" all-sender-ia "")'.format(
            __description__,
            __version__
        )

        typ, data = imap_obj.xatom('X-SCALIX-ID', arg)

        self.check_response(typ, data)

        return self.parse_string_pair(
            self.untagged_value(imap_obj, 'X-SCALIX-ID', '')
        )
