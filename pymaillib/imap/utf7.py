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
    from .dovecot_utils import imap4_utf7_decode, imap4_utf7_encode
except ImportError as _:
    warnings.warn('Failed to load dovecot utils. Load pure python '
                  'implementation', RuntimeWarning)
    from ._utf7 import imap4_utf7_decode, imap4_utf7_encode
