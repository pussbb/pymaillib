# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~
    Imap4 helper client library

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import warnings
from datetime import datetime
from threading import Lock, current_thread
from traceback import print_exception

from typing import Iterable, Any

from .commands.search import ImapSearchCommand
from .query.builders.search import SearchQueryBuilder
from .commands.store import ImapStoreCommand
from .query.builders.store import StoreQueryBuilder
from .query.builders.fetch import FetchQueryBuilder
from .commands.fetch import ImapFetchCommand
from .commands.folder import *
from .commands.folders import ImapFolderListCommand
from .commands.id import ImapIDCommand
from .commands.login import ImapLoginCommand
from .commands.namespace import Namespace
from .commands.scalix_id import ImaXScalixIDCommand
from .commands.unselect import ImapUnSelectFolderCommand
from .commands.wrapper import ImapLibWrapper
from .constants import IMAP4REV1_CAPABILITY_KEYS, IMAP4_COMMANDS
from .entity.folder import ImapFolder
from .entity.server import Namespaces
from .exceptions.base import ImapObjectNotFound, ImapIllegalStateException, \
    ImapUnsupportedCommand, ImapInvalidArgument
from .imap4 import IMAP4SSL, IMAP4, IMAP4Stream
from ..user import UserCredentials


class ImapClient(object):
    """Helper class to work with IMAP

    """

    def __init__(self, settings: dict, auth_data: UserCredentials):
        """Create new instance of imap client class. Automatically connect to
        the server, authorize user and get some details about the server

        :param settings: ProxyConfig
        :param auth_data: UserCredentials
        :return:
        """
        self.__opened = True
        self.__lock = Lock()
        self.capabilities = set()
        self.last_untagged_responses = {}
        self._count = 0
        self.__settings = settings
        self.__server_info = None
        self.__imap_obj = self.__init_imap_obj()
        self._update_capabilities(ImapLoginCommand(auth_data).run(
            self.__imap_obj)
        )
        self._update_server_info(self.__imap_obj)
        self._update_capabilities(self.__imap_obj.capabilities)

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

    def __getattr__(self, item) -> IMAP4:
        def wrapper(*args, **kwargs):
            return self.imaplib(item, *args, **kwargs)
        return wrapper

    def __repr__(self):
        return """Imap connection host: {host} port: {port} secure: {secure}.
        {capabilities}""".format(host=self.host, port=self.port,
                                 secure=self.secure,
                                 capabilities=self.__server_info)

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
        try:
            self.close()
        except Exception as excp:
            warnings.warn(excp, RuntimeWarning)

    @property
    def opened(self):
        """Indicates if connection to the IMAP is alive

        :return: True if connection established and alive otherwise False
        """
        return self.__opened

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
        socket connection or secured socket connection (SSL)

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

    def __init_imap_obj(self) -> IMAP4:
        """Creates new IMAP4 object

        :return: IMAP4
        """
        if not self.host:
            raise ImapInvalidArgument('Imap host must not be empty')
        if self.host.startswith('stream://'):
            return IMAP4Stream(self.host)
        if self.secure:
            return self.__init_imapssl_obj()
        if not self.port:
            self.__settings['port'] = str(imaplib.IMAP4_PORT)
        return IMAP4(host=self.host, port=self.port, timeout=self.timeout)

    def __init_imapssl_obj(self) -> IMAP4SSL:
        """ Creates new IMAP4 object with secure connection

        :return: IMAP4SSL
        """
        if not self.port:
            self.__settings['port'] = str(imaplib.IMAP4_SSL_PORT)

        return IMAP4SSL(host=self.host, port=self.port, keyfile=self.keyfile,
                         certfile=self.certfile, timeout=self.timeout)

    def folders(self) -> Iterable[ImapFolder]:
        """Get folder list from IMAP server. Executes LIST command at IMAP
        server.
        :return: list with ImapFolders
        """
        yield from self._simple_command(ImapFolderListCommand())

    def folder_stats(self, folder: ImapFolder) -> dict:
        """Get additional information for an folder which is not available
        in IMAP LIST command. Executes EXAMINE command at IMAP server.

        :param folder: ImapFolder
        :return: dict
        """
        return self._simple_command(ImapFolderDetailsCommand(folder))

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
        folders = self._simple_command(ImapFolderListCommand(pattern=name))
        if not folders:
            raise ImapObjectNotFound('Folder {} not found'.format(name))
        try:
            return next(folders)
        except StopIteration as _:
            raise ImapObjectNotFound('Folder {} not found'.format(name))

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
        return self.folder_by_name(
            self._simple_command(ImapCreateFolderCommand(name, parent)),
            safe=True
        )

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

    def fetch(self, folder: ImapFolder, query: FetchQueryBuilder):
        """Retries messages from a folder

        :param folder: ImapFolder object
        :param query: FetchQueryBuilder object
        """
        self.select_folder(folder)
        yield from self._simple_command(ImapFetchCommand(query))

    def store(self, query: StoreQueryBuilder):
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
        yield from self._simple_command(ImapStoreCommand(query))

    def search(self, query: SearchQueryBuilder):
        """

        :param query:
        :return:
        """
        yield from self._simple_command(ImapSearchCommand(query))

    def scalix_id(self) -> dict:
        """Gets additional information about current user. Will work only for
         Scalix IMAP server.

        :return: dict
        """
        return self._simple_command(ImaXScalixIDCommand())

    def namespace(self) -> Namespaces:
        """Returns imap server namespaces

        :return: Namespaces obj
        """
        return self._simple_command(Namespace())

    def imaplib(self, func, *args, **kwargs) -> Any:
        """Executes imapli.Imap4 functions

        :param func: imaplib Imap4 function name
        :param args: function arguments
        :param kwargs: function named arguments
        :return:
        """
        return self._simple_command(ImapLibWrapper(func, *args, **kwargs))
