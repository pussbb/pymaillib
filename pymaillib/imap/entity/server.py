# -*- coding: utf-8 -*-
"""

"""
from collections import namedtuple

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
