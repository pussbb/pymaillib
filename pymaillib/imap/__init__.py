# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~
    Imap4 client library

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

import imaplib

from . import utf7
from .exceptions import ImapClientError, ImapClientAbort, \
    ImapClientReadOnlyError

from .constants import IMAP_DEFAULTS

__version__ = '0.0.1 alpha'
__description__ = 'pymaillib IMAP$ client (python library).'
__license__ = 'WTFPL'

imaplib.Debug = 12
imaplib.IMAP4.error = ImapClientError
imaplib.IMAP4.abort = ImapClientAbort
imaplib.IMAP4.readonly = ImapClientReadOnlyError
