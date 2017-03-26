# -*- coding: utf-8 -*-
"""

"""
from collections import namedtuple

from . import SlotBasedImapEntity
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

    __slots__ = {'name', 'separator'}

    @staticmethod
    def build(data):
        raise NotImplementedError()


class Namespaces(SlotBasedImapEntity):
    __slots__ = ('private', 'other_users', 'public_folders')

    @staticmethod
    def build(data):
        private, other_users, public_folders = data

        def to_namespace_list(items):
            """Convert raw list data into list with Namespace's objects
            
            :param items: 
            :return: 
            """
            res = []
            if not items:
                return res
            for name, separator in items:
                res.append(ImapNamespace(name, separator))
            return res

        return Namespaces(private=to_namespace_list(private),
                          other_users=to_namespace_list(other_users),
                          public_folders=to_namespace_list(public_folders))

