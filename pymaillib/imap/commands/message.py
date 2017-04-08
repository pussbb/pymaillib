# -*- coding: utf-8 -*-
"""
    Imap4 Message manipulation
    ~~~~~~~~~~~~~~~~
    

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

import time
from typing import Any

from ..commands.folder import ImapCreateFolderCommand
from ..exceptions import ImapTryCreate
from ..entity.folder import ImapFolder
from ..exceptions import ImapInvalidArgument, ImapRuntimeError
from ..entity.email_message import EmailMessage
from . import ImapBaseCommand


class AppendMessageCommand(ImapBaseCommand):
    """

    """

    _COMMAND = 'APPEND'

    def __init__(self, message: EmailMessage, folder: ImapFolder,
                 flags: str=None):
        """
        Raises:
            ImapRuntimeError - if :param message is not instance of
                                EmailMessage

        :param message: EmailMessage
        :param folder: ImapFolder
        :return:
        """
        if not isinstance(message, EmailMessage):
            raise ImapInvalidArgument('message', message)
        self._message = message
        self.__folder = folder
        self.__flags = flags

    def run(self, imap_obj: imaplib.IMAP4, attemps=0):
        """Sends IMAP APPEND command.

        Raises: ImapRuntimeError - if command executions failed

        :param imap_obj: imaplib.IMAP4
        :return: Namespaces
        """

        try:
            typ, data = imap_obj.append(self.__folder.imap_name(), self.__flags,
                                        imaplib.Time2Internaldate(time.time()),
                                        self._message.as_bytes())
            self.check_response(typ, data)
        except ImapTryCreate as _:
            if attemps > 0:
                raise RecursionError('Could not append message because folder '
                                     'does not exists and we could not create '
                                     'it')
            ImapCreateFolderCommand(self.__folder).run(imap_obj)
            self.run(imap_obj, 1)
        else:
            if b'APPENDUID' in data[0]:
                append_uid, *_ = data[0].partition(b']')
                self._message.uid = int(append_uid.split()[-1])
            else:
                self._message.uid = 0
        return self._message


class UpdateMessageCommand(AppendMessageCommand):

    def run(self, imap_obj: imaplib.IMAP4, attemps=0):
        if not self._message.uid:
            raise ImapRuntimeError('Message does not have previous UID')

        old_uid = self._message.uid
        super().run(imap_obj)
        if self._message.uid == int(old_uid):
            raise ImapRuntimeError('Message new UID is the same as old one')
        DeleteMessageCommand(str(old_uid)).run(imap_obj)
        return self._message


class DeleteMessageCommand(AppendMessageCommand):
    _COMMAND = 'STORE'

    def __init__(self, uids: Any):
        if isinstance(uids, EmailMessage):
            uids = uids.uid
        self.__uids = str(uids)

    def run(self, imap_obj: imaplib.IMAP4):
        typ, data = imap_obj.uid('STORE', self.__uids, '+FLAGS', '\\Deleted')
        self.check_response(typ, data)
        typ, data = imap_obj.expunge()
        self.check_response(typ, data)
        return True
