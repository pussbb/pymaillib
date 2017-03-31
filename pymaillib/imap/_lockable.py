# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~
    Imap4 client library

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib
import warnings
from threading import current_thread, Lock
from datetime import datetime
from traceback import print_exception
from typing import Any

from .constants import IMAP4_COMMANDS, IMAP4REV1_CAPABILITY_KEYS
from .commands import ImapBaseCommand
from .exceptions import ImapUnsupportedCommand, ImapIllegalStateException


class LockableImapObject(object):
    """Implements functionality which gives ability work with IMAP in context
    and disable executes any IMAP commands outside context. Callers must use
    ``` with self as client: ``` statement to work with IMAP

    """

    def __init__(self, obj: imaplib.IMAP4):
        """ create new instance

        :param obj: imaplib.IMAP4 object
        :return:
        """
        self.__opened = True
        self.__lock = Lock()
        self.capabilities = set()
        self.last_untagged_responses = {}
        self.__imap_obj = obj
        self._count = 0
        self._update_capabilities(self.__imap_obj.capabilities)

    def _update_capabilities(self, capabilities: list):
        """Updates list of available command at IMAP server

        :param capabilities: None or list with IMAP commands
        :return: None
        """

        if not capabilities:
            return
        self.capabilities |= set(capabilities)
        if IMAP4REV1_CAPABILITY_KEYS & self.capabilities:
            self.capabilities = self.capabilities | IMAP4_COMMANDS
        if 'X-SCALIX-1' in self.capabilities:
            self.capabilities.add('X-SCALIX-ID')

    def __enter__(self):
        if not self.__lock.locked():
            self.__lock.acquire()

        self._count += 1

        if __debug__:
            print('Lock acquired ', current_thread().name,
                  datetime.now().isoformat())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            print_exception(exc_type, exc_val, exc_tb)

        self._count -= 1
        if not self._count:
            self.__lock.release()
        if __debug__:
            print('Lock released ', current_thread().name,
                  datetime.now().isoformat())
        return False

    def _simple_command(self, command: ImapBaseCommand) -> Any:
        """Generic function to execute Imap commands

        Raises:
            - ImapUnsupportedCommand if server does not support command
            - ImapRuntimeError if caller tries to execute command without
                acquiring context
            - ImapRuntimeError if connection to the server was closed and any
                requests will fail.

        :param command: object instanceof ImapBaseCommand
        :return:
        """

        if not self.__lock.locked():
            raise ImapIllegalStateException('Working outside context')
        if not self.supports(command.name):
            raise ImapUnsupportedCommand(command)

        result = command.run(self.__imap_obj)
        self.last_untagged_responses = self.__imap_obj.untagged_responses

        if self.last_untagged_responses:
            warnings.warn('Data left {}'.format(self.last_untagged_responses),
                          RuntimeWarning)
        return result

    def supports(self, command_name: str):
        """Checks if IMAP server support IMAP command or not. All supported
        IMAP commands by the server in :attr:capabilities

        :param command_name: IMAP command name ignore letter case
        :return: True if IMAP command is supported be IMAP server otherwise
            False
        """
        return command_name.upper() in self.capabilities

    def close(self):
        """Close current connection to the IMAP server

        :return:
        """
        if not self.__opened:
            return
        self.__opened = False
        if self.__imap_obj:
            self.__imap_obj.shutdown()

    def __del__(self):
        self.close()

    @property
    def opened(self):
        """Indicates if connection to the IMAP is alive

        :return: True if connection established and alive otherwise False
        """
        return self.__opened
