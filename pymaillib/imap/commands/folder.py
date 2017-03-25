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
from typing import AnyStr

from ..exceptions import ImapRuntimeError
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


class ImapCreateFolderCommand(ImapBaseCommand):
    """Executes  IMAP Create cammand

    """

    _COMMAND = 'CREATE'

    def __init__(self, folder_name: AnyStr, parent: ImapFolder):
        """Creates new instance of the class specifying for what folder command
        will be executed.

        :param folder_name: AnyStr
        :param parent: ImapFolder
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


class ImapRenameFolderCommand(ImapBaseCommand):
    """Executes  IMAP RENAME cammand to rename folder

    """

    _COMMAND = 'RENAME'

    def __init__(self, old_folder: ImapFolder, folder_name: AnyStr,
                 parent: ImapFolder):
        """Creates new instance of the class specifying for what folder command
        will be executed.

        :param old_folder: ImapFolder
        :param folder_name: AnyStr new folder name
        :param parent: ImapFolder
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
