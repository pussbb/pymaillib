# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~
    Imap4 helper client library

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from typing import Iterable

from . imap4 import IMAP4_SSL, IMAP4
from .commands.namespace import Namespace
from .entity.email_message import ImapEmailMessage
from .fetch_query_builder import FetchQueryBuilder
from .exceptions import ImapObjectNotFound
from ..user import UserCredentials
from ._lockable import LockedImapObject
from .commands.folder import *
from .commands.unselect import ImapUnSelectFolderCommand
from .commands.fetch import ImapFetchCommand
from .commands.id import ImapIDCommand
from .commands.scalix_id import ImaXScalixIDCommand
from .commands.folders import ImapFolderListCommand
from .commands.login import ImapLoginCommand
from .entity.folder import ImapFolder


class ImapClient(LockedImapObject):
    """Helper class to work with IMAP

    """

    def __init__(self, settings: dict, auth_data: UserCredentials):
        """Create new instance of imap client class. Automatically connect to
        the server, authorize user and get some details about the server

        :param settings: ProxyConfig
        :param auth_data: UserCredentials
        :return:
        """
        self.__settings = settings
        self.__server_info = None
        imap_obj = self.__init_imap_obj()
        super().__init__(obj=imap_obj)
        self._update_capabilities(ImapLoginCommand(auth_data).run(imap_obj))
        self._update_server_info(imap_obj)

    def _update_server_info(self, imap_obj):
        """Executes :class:ImapIDCommand to identify client library and
        get server info. This function must be executed once per session.
        Please reuse it if it's really necessary.

        :param imap_obj: object
        :return:
        """
        self.__server_info = ImapIDCommand().run(imap_obj)

    @property
    def server_info(self):
        """Returns server related information

        :return: ServerInfo
        """
        return self.__server_info

    @property
    def host(self):
        """Returns host used for connection to the IMAP server

        :return: string
        """
        return self.__settings.get('host')

    @property
    def secure(self):
        """Flag which describes what type of connection was used - simple
        socket connection or secured sockect connection (SSL)

        :return: boolean
        """
        return self.__settings.get('secure')

    @property
    def port(self):
        """Returns port number for connection

        :return: int
        """
        return self.__settings.get('port')

    @property
    def keyfile(self):
        """Optional attribute for a secured connection type.
        PEM formatted file that contains your private key

        :return: str
        """
        return self.__settings.get('keyfile')

    @property
    def certfile(self):
        """Optional attribute for a secured connection type.
        PEM formatted certificate chain file

        :return: str
        """
        return self.__settings.get('certfile')

    @property
    def timeout(self):
        """Socket timeout
        
        :return: 
        """
        return self.__settings.get('timeout', 60)

    def __init_imap_obj(self) -> imaplib.IMAP4:
        """Creates new IMAP4 object

        :return:  imaplib.IMAP4
        """
        if self.secure:
            return self.__init_imapssl_obj()
        if not self.port:
            self.__settings['port'] = str(imaplib.IMAP4_PORT)
        return IMAP4(host=self.host, port=self.port, timeout=self.timeout)

    def __init_imapssl_obj(self) -> imaplib.IMAP4_SSL:
        """ Creates new IMAP4 object with secure connection

        :return: imaplib.IMAP4_SSL
        """
        if not self.port:
            self.__settings['port'] = str(imaplib.IMAP4_SSL_PORT)

        return IMAP4_SSL(host=self.host, port=self.port, keyfile=self.keyfile,
                         certfile=self.certfile, timeout=self.timeout)

    def folders(self, with_stats=False) -> Iterable[ImapFolder]:
        """Get folder list from IMAP server. Executes LIST command at IMAP
        server.

        :param with_stats: boolean indicates get details for a folder or not
        :return: list with ImapFolders
        """
        res = self._simple_command(ImapFolderListCommand())
        if with_stats:
            res = [self.update_folder_info(folder) for folder in res]
        return res

    def folder_stats(self, folder: ImapFolder) -> dict:
        """Get additional information for an folder which is not available
        in IMAP LIST command. Executes EXAMINE command at IMAP server.

        :param folder: ImapFolder
        :return: dict
        """

        resp = self._simple_command(ImapFolderDetailsCommand(folder))
        if self.supports('unselect'):
            self.un_select_folder()
        return resp

    def un_select_folder(self):
        """Executes UNSELECT folder

        """
        self._simple_command(ImapUnSelectFolderCommand())

    def update_folder_info(self, folder: ImapFolder) -> ImapFolder:
        """Updates additional information about folder for an ImapFolder object.

        :param folder: ImapFolder
        :return: ImapFolder
        """
        if not folder.selectable:
            return folder
        folder.stats = self.folder_stats(folder)
        return folder

    def folder_by_name(self, name: str, safe=False) -> ImapFolder:
        """Search for a folder by name

        Raises:
                - ImapObjectNotFound if folder not found

        :param name: str folder name
        :param safe: bool if folder name is escaped or not. Default
            value is False and it will try to escape string
        :return: ImapFolder folder
        """
        if not name:
            raise ImapRuntimeError('Folder name is empty')
        if not safe:
            name = ImapFolder.escape_name(name)
        folders = list(
            self._simple_command(ImapFolderListCommand(pattern=name))
        )
        if not folders:
            raise ImapObjectNotFound('Folder {} not found'.format(name))
        return folders[0]

    def folder_exists(self, name: str) -> bool:
        """Checks if folder exists at IMAP server

        :param name: str folder name
        :return: True if folder exists at IMAP server otherwise False
        """
        try:
            self.folder_by_name(name)
        except ImapObjectNotFound as _:
            return False
        else:
            return True

    def rename_folder(self, folder: ImapFolder, new_folder_name: str,
                      parent_folder: ImapFolder):
        """Change namr of the existing folder name

        :param parent_folder: ImapFolder
        :param folder: ImapFolder instance
        :param new_folder_name: AnyStr
        :return:
        """
        res = self._simple_command(
            ImapRenameFolderCommand(folder, new_folder_name, parent_folder)
        )
        return self.folder_by_name(res, safe=True)

    def create_folder(self, name: str, parent=None):
        """Create new folder at IMAP server

        :param name:
        :param parent:
        :return: ImapFolder instance new created folder
        """

        res = self._simple_command(ImapCreateFolderCommand(name, parent))
        return self.folder_by_name(res, safe=True)

    def delete_folder(self, folder: ImapFolder):
        """Delete existing folder from IMAP

        :param folder: ImapFolder instance
        """
        return self._simple_command(ImapDeleteFolderCommand(folder))

    def select_folder(self, folder: ImapFolder) -> None:
        """Select folder

        :param folder:
        """
        return self._simple_command(ImapSelectFolderCommand(folder))

    def messages(self, folder: ImapFolder, query: FetchQueryBuilder,
                 stay=True):
        """Retries messages from a folder

        :param folder: ImapFolder object
        :param query: FetchQueryBuilder object
        :param stay: True or False unselect folder or not
        """
        self.select_folder(folder)
        res = self._simple_command(ImapFetchCommand(query))
        if not stay and self.supports('unselect'):
            self.un_select_folder()
        yield from [ImapEmailMessage.from_dict(item) for item in res]

    def store(self):
        """To avoid all those calls to STORE trying calling it with multiple
         message ids. You can either pass a comma separate listed
         (e.g. "1,2,3,4"), ranges of message ids (e.g. "1:10") or a
         combination of both (e.g. "1,2,5,1:10"). Note that most servers
         seem to have a limit on the number of message ids allowed per call
         so you'll probably still need to chunk the ids into blocks (of say 200
         messages) and call STORE multiple times. This will still be much, much
          faster than calling STORE per message.

        :return:
        """

    def scalix_id(self) -> dict:
        """Gets additional information about current user. Will work only for
         Scalix IMAP server.

        :return: dict
        """
        return self._simple_command(ImaXScalixIDCommand())

    def namespace(self):
        return self._simple_command(Namespace())

    def __repr__(self):
        try:
            opened = self.opened
        except KeyError as _:
            opened = False
        return """Imap connection host: {host} port: {port} secure: {secure}
        opened {opened}. {capabilities}""".format(
            host=self.host,
            port=self.port,
            secure=self.secure,
            opened=opened,
            capabilities=self.__server_info
        )
