# -*- coding: utf-8 -*-
"""
    Mail User
    ~~~~~~~~~~~~~~~~
    Mail User contains classes for user related information

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import collections


UserCredentials = collections.namedtuple(
    'UserCredentials',
    ['username', 'password']
)

UserInfo = collections.namedtuple(
    'UserInfo',
    ['auth_id', 'display_name', 'mail_address', 'global_id']
)
