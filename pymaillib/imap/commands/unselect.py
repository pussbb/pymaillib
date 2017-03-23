# -*- coding: utf-8 -*-
"""
    Imap4 UNSELECT Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP UNSELECT cammand can be used to close
    the current mailbox in an IMAP server

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from . import ImapBaseCommand


class ImapUnSelectFolderCommand(ImapBaseCommand):
    """Executes  IMAP UNSELECT cammand can be used to close
    the current mailbox in an IMAP server

    """

    _COMMAND = 'UNSELECT'

    def error_message(self):
        """Error message for UNSELECT command

        :return: str
        """
        return 'Could not un select folder.'

    def run(self, imap_obj: imaplib.IMAP4):
        """Executes Executes  IMAP UNSELECT cammand can be used to close
        the current mailbox in an IMAP server

        Raises: ImapRuntimeError - if command executions failed

        :param imap_obj: imaplib.IMAP4
        :return:  None
        """
        self.check_response(*imap_obj.xatom('UNSELECT'))
