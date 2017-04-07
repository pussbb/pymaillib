# -*- coding: utf-8 -*-
"""
    Imap4 Store Query Builder
    ~~~~~~~~~~~~~~~~


    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from ...exceptions import ImapRuntimeError
from . import BaseQueryBuilder


class StoreQueryBuilder(BaseQueryBuilder):
    """Creates valid STORE imap command query

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__silent = False
        self.__flags = set()
        self.__cmd = 'FLAGS'

    @property
    def silent(self) -> bool:
        """

        :return:
        """
        return self.__silent

    @silent.setter
    def silent(self, value):
        """

        :param value:
        :return:
        """
        self.__silent = bool(value)

    def __set_items(self, cmd, flags: set):
        """

        :param cmd:
        :param flags:
        :return:
        """
        self.__cmd = cmd
        self.__flags = set(flags)

    def replace(self, *args):
        """

        :return:
        """
        self.__set_items('FLAGS', args)
        return self

    def remove(self, *args):
        """

        :return:
        """
        self.__set_items('-FLAGS', args)
        return self

    def add(self, *args):
        """

        :return:
        """
        self.__set_items('+FLAGS', args)
        return self

    def build(self):
        if not self.__flags:
            raise ImapRuntimeError('You have not specified message FLAGS')
        cmd = self.__cmd
        if self.__silent:
            cmd += '.SILENT'
        return self._build_range(), cmd, '({})'.format(
            ' '.join([item for item in self.__flags])
        )

    def __repr__(self):
        return ' '.join(self.build())
