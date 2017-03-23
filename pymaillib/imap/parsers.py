# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~


    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

try:
    from .pyimapparser import *
except ImportError as _:
    from ._parsers import *
