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

from .exceptions.base import ImapClientError, ImapClientAbort, \
    ImapClientReadOnlyError, ImapByeByeException, ImapRuntimeError

imaplib.IMAP4.error = ImapClientError
imaplib.IMAP4.abort = ImapClientAbort
imaplib.IMAP4.readonly = ImapClientReadOnlyError


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

    def _check_bye(self):
        try:
            super()._check_bye()
        except ImapClientError as exp:
            raise ImapByeByeException(exp)

    def open(self, *args, **kwargs):
        try:
            super().open(*args, **kwargs)
        except BaseException as excp:
            raise ImapRuntimeError(excp)

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
        try:
            return self.ssl_context.wrap_socket(sock,
                                                server_hostname=self.host)
        except Exception as excp:
            raise ImapRuntimeError(excp)


class IMAP4Stream(imaplib.IMAP4_stream):

    def __init__(self, command: str):
        super().__init__(command=command.replace('stream:/', '', 1))
