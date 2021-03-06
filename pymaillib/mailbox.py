# -*- coding: utf-8 -*-
"""
    UserMailbox
    ~~~~~~~~~~~~~~~~
    UserMailbox

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import warnings

import re
from typing import Any

from .settings import Config
from .user import UserCredentials
from .imap.client import ImapClient
from .imap.exceptions import ImapReferralsException

IMAP_URL_PATTERN = rb'(?P<protocol>.+?)://(?P<username>.+?);' \
                   rb'(?P<auth>.+?)@(?P<host>.*)'


class UserMailbox(object):
    """ Generic class to hold Imap and Smtp objects in one class.


    """

    def __init__(self, username: Any, password: Any, config: Config):
        """Creates new instance of the class for specified user.

        Rasies:
            - AssertionEror if provided username or password is empty

        :param username:
        :param password:
        :return:
        """
        self.__imap_store = None
        assert username, 'Username cannot be empty'
        assert password, 'Username cannot be empty'
        self.__auth_data = UserCredentials(username, password)
        self.__config = config

    def clone(self) -> 'UserMailbox':
        return UserMailbox(self.__auth_data.username,
                           self.__auth_data.password, self.__config)

    @property
    def auth_data(self) -> UserCredentials:
        """Get credentiols for an instance

        :return: UserCredentials
        """
        return self.__auth_data

    def check(self, auth_data: UserCredentials):
        return self.__auth_data.username == auth_data.username and \
               self.__auth_data.password == auth_data.password

    def imap(self, unselect: bool=False) -> ImapClient:
        """Creates or returns cached instance if ImapClient class

        :return: IMapClient instance
        """
        if self.__imap_store and self.__imap_store.opened:
            if unselect:
                with self.__imap_store as imap:
                    imap.release_current_folder()
            return self.__imap_store

        self.__imap_store = self.get_imap_client()
        return self.__imap_store

    def get_imap_client(self):
        return self.__create_imap_connection()

    def __create_imap_connection(self, attempts=None):
        if attempts is None:
            attempts = 0
        if attempts > 10:
            raise RecursionError('Giving up with imap referrals.')
        try:
            return ImapClient(self.__config['imap'], self.__auth_data)
        except ImapReferralsException as ex:
            _res = re.search(IMAP_URL_PATTERN, ex.imap_url)
            self.__config['imap']['host'] = _res.group('host')
            return self.__create_imap_connection(attempts + 1)

    def smtp(self):
        raise NotImplementedError

    def __del__(self):
        try:
            self.close()
        except Exception as exp:
            warnings.warn(exp, RuntimeWarning)

    def close(self):
        """Clean up. Close all conections et.

        """
        self.close_imap()
        self.close_smtp()

    def close_imap(self):
        """Close current imap connection

        :return:
        """
        if not hasattr(self, '__imap_store'):
            return
        self.__imap_store.close()
        self.__imap_store = None

    def close_smtp(self):
        """Close current SMTP connection

        :return:
        """
        pass
        # raise NotImplementedError

    def mailboxes(self) -> dict:
        """Get list of folders from IMAP server

        :return: dict where folder direct ref is key and value is ImapFolder
            instance
        """
        result = {}
        with self.imap() as client:
            for folder in client.folders():
                result[folder.direct_ref] = folder
        return result

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Mail session for user "{auth.username}"'.format(
            auth=self.auth_data
        )
