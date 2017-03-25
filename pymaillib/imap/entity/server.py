# -*- coding: utf-8 -*-
"""

"""
from collections import namedtuple

from imap.entity import SlotBasedImapEntity
from ...user import UserInfo

ServerInfo = namedtuple('ServerInfo', ['imap_name', 'imap_version', 'host',
                                       'port', 'os', 'date', 'os_version',
                                       'user_info'])


def from_id_command(data: dict, host: str, port: int) -> ServerInfo:
    """Parse raw string and construct some object

    :param data:
    :param host:
    :param port:
    :return:
    """
    user_info = UserInfo(
        data.get('auth-id'),
        data.get('display-name'),
        data.get('mail-address'),
        data.get('global-unique-id'),
    )

    return ServerInfo(
        data.get('name'),
        data.get('version'),
        host,
        port,
        data.get('os'),
        data.get('date'),
        data.get('os-version'),
        user_info
    )

class ImapNamespace(SlotBasedImapEntity):
    __slots__ = {'__name', '__separator'}

    def __init__(self, name, separator):
        self.__name = name
        self.__separator = separator

    @property
    def name(self):
        return self.__name

    @property
    def separator(self):
        return self.__separator

    def dump(self):
        return {
            'name': self.__name,
            'separator': self.__separator,
        }


class Namespaces(SlotBasedImapEntity):
    __slots__ = ('_private', '_other_users', '_public_folders')

    def __init__(self, private, other_users, public_folders):
        self._private = private
        self._other_users = other_users
        self._public_folders = public_folders

    def dump(self):
        return {
            'private': self._private,
            'other_users': self._other_users,
            'public_folders': self._public_folders
        }

    @staticmethod
    def parse(data):
        private, other_users, public_folders = data
        def to_namespace_list(items):
            res = []
            if not items:
                return res
            for name, separator in items:
                res.append(ImapNamespace(name, separator))
            return res

        return Namespaces(private=to_namespace_list(private),
                          other_users=to_namespace_list(other_users),
                          public_folders=to_namespace_list(public_folders))

