# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~


    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import warnings

try:
    from .pyimapparser import *
except ImportError as _:
    warnings.warn('Failed to load c++ parser module. Using slower version'
                  ' of parser', RuntimeWarning)
    from ._parsers import *
