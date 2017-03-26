# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~
    Imap4 helper client library

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib
import socket

import collections

from datetime import datetime

from typing import Any


def _profile(func):
    if func.__func__.__name__.startswith('_'):
        return func

    def wrapper(*args, **kwargs):
        start = datetime.now()
        try:
            return func(*args, **kwargs)
        finally:
            print('Function "{}" done in {}.'.format(func.__func__,
                                                     datetime.now() - start),
                  flush=True)
    return wrapper


class IMAP4(imaplib.IMAP4):

    def __init__(self, host: Any, port: int, timeout: int=60):
        self._timeout = timeout
        super().__init__(host, port)

    def _create_socket(self):
        return socket.create_connection((self.host, self.port), self._timeout)

    if __debug__:
        def __getattribute__(self, item):
            item = super().__getattribute__(item)
            if imaplib.Debug > 5 and isinstance(item, collections.Callable):
                    return _profile(item)
            return item


class IMAP4_SSL(imaplib.IMAP4_SSL):

    def __init__(self, host: Any, port: int, keyfile=None, certfile=None,
                 ssl_context=None, timeout: int=60):
        self._timeout = timeout
        super().__init__(host, port, keyfile, certfile, ssl_context)

    def _create_socket(self):
        sock = IMAP4._create_socket(self)
        return self.ssl_context.wrap_socket(sock,
                                            server_hostname=self.host)
