# -*- coding: utf-8 -*-
"""
    Imap4 ID Command
    ~~~~~~~~~~~~~~~~
    Executes IMAP ID command to identify client and get server information

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from ..entity.server import from_id_command
from . import ImapBaseCommand
from .. import __version__, __description__


class ImapIDCommand(ImapBaseCommand):
    """Executes IMAP ID command to identify client and get server information

    """

    _COMMAND = 'ID'

    def error_message(self):
        """Default error message for unsuccessful ID command

        :return: str
        """
        return 'Could not determine server info.'

    def run(self, imap_obj: imaplib.IMAP4):
        """Sends IMAP ID command.

        Raises: ImapRuntimeError - if command executions failed

        :param imap_obj: imaplib.IMAP4
        :return: ServerInfo
        """
        typ, data = imap_obj.xatom(
            'ID',
            '("name" "{}" "version" "{}")'.format(__description__, __version__)
        )
        self.check_response(typ, data)
        data = self.parse_string_pair(
            self.untagged_value(imap_obj, 'ID', '')
        )
        return from_id_command(data, imap_obj.host, imap_obj.port)
