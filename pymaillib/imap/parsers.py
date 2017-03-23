# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~


    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import warnings

try:
    from .pyimapparser import ResponseTokenizer, parse_atom_name, get_part
except ImportError as _:
    warnings.warn('Failed to load c++ parser module. Using slower version'
                  ' of parser', RuntimeWarning)
    from ._parsers import ResponseTokenizer, parse_atom_name, get_part

from . import constants

__DEFAULT_ATOM_PARSER = constants.FETCH_ITEMS.get(b'X-')


def tokenize_atom_response(line: bytes, literals: list):
    """

    :param line: bytes
    :param literals: list
    :return: generator
    """
    parser = ResponseTokenizer(line, literals)
    yield 'SEQ', parser.__next__()
    rest_items = iter(parser.__next__())
    for item in rest_items:
        name, atom_data = parse_atom_name(item)
        atom = constants.FETCH_ITEMS.get(name, __DEFAULT_ATOM_PARSER)
        yield name.decode(), atom.parse(atom_data, rest_items.__next__())


class ListTokenizer(ResponseTokenizer):
    __slots__ = ()
