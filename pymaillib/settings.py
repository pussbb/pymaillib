# -*- coding: utf-8 -*-
"""
    pymaillib
    ~~~~~~~~~~~~~~~~
    Mail client

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

import os
from configparser import ConfigParser
from .imap.constants import IMAP_DEFAULTS

_DEFAULT_OPTIONS = {
    'imap': IMAP_DEFAULTS,
}

CONFIG = ConfigParser(allow_no_value=True)
__CONFIG_FILE = os.environ.get('PYMAILLIB_CONFIG', './sxmail.ini')
CONFIG.read_dict(_DEFAULT_OPTIONS)

filename = os.path.realpath(os.path.expanduser(__CONFIG_FILE))
if os.path.exists(filename):
    CONFIG.read_file(open(filename))
# TODO uncoment it when we will be ready for this
"""
else:
    raise RuntimeError(
        "Config file was not found (expected to load from {filename})".format(
            filename=filename
        )
    )
"""

IMAP_CONFIG = {}
imap_prop_func_map = {
    'secure': 'getboolean',
    'port': 'getint'
}
for key in CONFIG['imap']:
    func = imap_prop_func_map.get(key, 'get')
    IMAP_CONFIG[key] = getattr(CONFIG['imap'], func)(key)

smtp_prop_func_map = {
    'secure': 'getboolean',
    'port': 'getint'
}
