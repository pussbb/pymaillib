# -*- coding: utf-8 -*-
"""
    Imap4 Delete Folder Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP DELETE cammand to delete folder

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from ..exceptions import ImapRuntimeError
from ..entity.folder import ImapFolder
from . import ImapBaseCommand


class ImapDeleteFolderCommand(ImapBaseCommand):
    """Executes  IMAP DELETE cammand to rename folder

    """

    _COMMAND = 'DELETE'

    def __init__(self, folder: ImapFolder):
        """Creates new instance of the class specifying for what folder command
        will be executed.

        Raises:
             - ImapRuntimeError is folder not selectable or can not be deleted

        :param folder: folder object
        :return:
        """
        if not folder.editable:
            raise ImapRuntimeError('Folder {} is not editable'.format(folder))

        self.__folder_name = folder.imap_name()

    def error_message(self):
        """Default error message during folder deletion

        :return: str
        """
        return 'Could not delete mailbox {}. '.format(self.__folder_name)

    def run(self, imap_obj: imaplib.IMAP4):
        """Deletes folder from imap server

        :param imap_obj:
        :return:
        """
        typ, data = imap_obj.delete(self.__folder_name)
        self.check_response(typ, data)
        return True
