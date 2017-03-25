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
from copy import deepcopy

from .imap.constants import IMAP_DEFAULTS


CONFIG_PROP_FUNC_MAP = {
    'secure': 'getboolean',
    'port': 'getint'
}


class Config(dict):

    def __init__(self, defaults: dict=None):
        super().__init__(defaults or {})
        self['imap'] = {**deepcopy(IMAP_DEFAULTS), **self.get('imap', {})}

    def from_envvar(self, key: str) -> 'Config':
        value = os.environ.get(key)
        if not value:
            raise RuntimeError('Environment key {} is empty'
                               ' or not found'.format(key))
        filename = os.path.realpath(os.path.expanduser(value))
        if not os.path.exists(filename):
            raise RuntimeError('File {} does not exists'.format(filename))
        return self.from_config_file(filename)

    def from_config_file(self, filename: str) -> 'Config':
        config_parser = ConfigParser(allow_no_value=True)
        config_parser.read(filename)
        for section in config_parser.sections():
            section_data = {}
            for key in config_parser[section]:
                func = CONFIG_PROP_FUNC_MAP.get(key, 'get')
                section_data[key] = getattr(config_parser[section], func)(key)
            self[section] = {**self.get(section, {}), **section_data}
        return self
