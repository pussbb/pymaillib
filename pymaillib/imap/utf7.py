# -*- coding: utf-8 -*-
"""
    Imap4 Utils
    ~~~~~~~~~~~~~~~~
    Some helpers functions maybe you not need them but they are common
    and spread all over the IMAP module

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

import warnings

try:
    from . import dovecot_utils as imap_utf7_codec
except ImportError as _:
    warnings.warn('Failed to load dovecot utils. Load pure python '
                  'implementation', RuntimeWarning)
    from . import _utf7 as imap_utf7_codec


def imap4_utf7_encode(data):
    """Encode a folder name using IMAP modified UTF-7 encoding.

    Input is unicode; output is bytes (Python 3) or str (Python 2). If
    non-unicode input is provided, the input is returned unchanged.
    """
    if not isinstance(data, str):
        return data
    return imap_utf7_codec.imap4_utf7_encode(data)


def imap4_utf7_decode(data):
    """Decode a folder name from IMAP modified UTF-7 encoding to unicode.

    Input is bytes (Python 3) or str (Python 2); output is always
    unicode. If non-bytes/str input is provided, the input is returned
    unchanged.
    """

    if not isinstance(data, bytes):
        return bytearray(data, 'utf-8')
    return imap_utf7_codec.imap4_utf7_decode(data)
