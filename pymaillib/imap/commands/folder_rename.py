# -*- coding: utf-8 -*-
"""
    Imap4 Rename Folder  Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP RENAME cammand to rename an existing folder

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from ..exceptions import ImapRuntimeError
from ..entity.folder import ImapFolder
from . import ImapBaseCommand


class ImapRenameFolderCommand(ImapBaseCommand):
    """Executes  IMAP RENAME cammand to rename folder

    """

    _COMMAND = 'RENAME'

    def __init__(self, old_folder: ImapFolder, folder_name: str,
                 parent: ImapFolder):
        """Creates new instance of the class specifying for what folder command
        will be executed.

        :param folder: string folder name
        :return:
        """
        if not old_folder.editable:
            raise ImapRuntimeError(
                'Folder {} is not editable'.format(old_folder)
            )

        self.__old_name = old_folder.imap_name()
        self.__new_name = ImapFolder.build_folder_name(folder_name, parent)

    def error_message(self):
        """Default error message during moving or renaming folder

        :return: str
        """
        return 'Could not rename mailbox from {} to {}. '.format(
            self.__old_name,
            self.__new_name
        )

    def run(self, imap_obj: imaplib.IMAP4):
        """renames folder at imap server

        :param imap_obj:
        :return: renamed folder name
        """
        typ, data = imap_obj.rename(self.__old_name, self.__new_name)
        self.check_response(typ, data)
        return self.__new_name
