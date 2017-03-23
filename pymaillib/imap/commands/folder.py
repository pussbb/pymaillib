# -*- coding: utf-8 -*-
"""
    Imap4 Folder details Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP EXAMINE cammand for an folder and returns response in
    human readable/usable form

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.

    STATUS (EXISTS ......)
"""
import imaplib

from ..constants import FOLDER_UNTAGGED_KEYS
from ..entity.folder import ImapFolder
from . import ImapBaseCommand


class ImapFolderDetailsCommand(ImapBaseCommand):
    """Executes  IMAP EXAMINE cammand for an folder and returns response in
    human readable/usable form

    """

    _COMMAND = 'EXAMINE'

    def __init__(self, folder: ImapFolder, readonly=True):
        """Creates new instance of the class specifying for what folder command
        will be executed.

        :param folder: string folder name
        :return:
        """
        self.__readonly = readonly
        self.__folder = folder.imap_name()

    def error_message(self):
        """Default error message for entering some mailbox(folder)

        :return: str
        """
        return 'Could not select folder {0}'.format(self.__folder)

    def run(self, imap_obj: imaplib.IMAP4):
        """Executes EXAMINE Imap command for a specified folder and parses
         response from an server response.

        Raises: ImapRuntimeError - if command executions failed

        :param imap_obj: imaplib.IMAP4
        :return: dict
        """
        status, data = imap_obj.select(self.__folder, readonly=self.__readonly)
        self.check_response(status, data)

        result = {'EXISTS': int(data[0])}
        for attr in FOLDER_UNTAGGED_KEYS:
            value = self.untagged_value(imap_obj, attr)
            if value:
                if value and attr in ('PERMANENTFLAGS', 'FLAGS'):
                    value = value.strip(b'()').split(b' ')
                else:
                    value = int(value)
            result[attr] = value

        return result


class ImapSelectFolderCommand(ImapFolderDetailsCommand):
    """Executes  IMAP select cammand for an folder and returns response in
    human readable/usable form

    """

    _COMMAND = 'SELECT'

    def __init__(self, folder: ImapFolder):
        super(ImapSelectFolderCommand, self).__init__(folder, False)
