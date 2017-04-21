# -*- coding: utf-8 -*-
"""
    Imap4 Folder List Command
    ~~~~~~~~~~~~~~~~
    Executes IMAP LIST cammand to get  a list of all folders in mailbox

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from ..entity.folder import ImapFolder
from . import ImapBaseCommand


class ImapFolderListCommand(ImapBaseCommand):
    """Executes IMAP LIST cammand to get  a list of all folders in mailbox

    """

    _COMMAND = 'LIST'

    def __init__(self, directory: str='""', pattern:str ='*'):
        self.__directory = directory
        self.__pattern = pattern

    def error_message(self):
        """Default error message for unsuccessful LIST command

        :return: str
        """
        return 'Could not get folder list with search pattern directory={}' \
               ' pattern={}. '.format(self.__directory, self.__pattern)

    def run(self, imap_obj: imaplib.IMAP4):
        """Runs LIST command.

        Raises:
            - ImapRuntimeError - if command executions failed

        :param imap_obj: imaplib.IMAP4
        :return: iterable with ImapFolder items
        """
        typ, data = imap_obj.list(self.__directory, self.__pattern)
        self.check_response(typ, data)
        for line in filter(None, data):
            yield ImapFolder.build(line)
