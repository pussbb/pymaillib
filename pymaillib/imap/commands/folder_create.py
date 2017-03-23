# -*- coding: utf-8 -*-
"""
    Imap4 Create Folder Command
    ~~~~~~~~~~~~~~~~
    Executes  IMAP Create cammand to delete folder

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib
from typing import AnyStr

from ..entity.folder import ImapFolder
from . import ImapBaseCommand


class ImapCreateFolderCommand(ImapBaseCommand):
    """Executes  IMAP Create cammand

    """

    _COMMAND = 'CREATE'

    def __init__(self, folder_name: AnyStr, parent: ImapFolder):
        """Creates new instance of the class specifying for what folder command
        will be executed.

        :param folder: folder object
        :return:
        """
        self.__folder_name = ImapFolder.build_folder_name(folder_name, parent)

    def error_message(self):
        """Default error message during folder creation

        :return: str
        """
        return 'Could not create mailbox {}. '.format(self.__folder_name)

    def run(self, imap_obj: imaplib.IMAP4):
        """Executes CREATE imap command

        :param imap_obj:
        :return: name of created folder
        """
        typ, data = imap_obj.create(self.__folder_name)
        self.check_response(typ, data)
        return self.__folder_name
