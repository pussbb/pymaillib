# -*- coding: utf-8 -*-
"""
    Imap4
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

from __future__ import generator_stop

from .utils import byte2int
from .exceptions import ImapResponseParserError


def parse_value(val: bytes):
    """Parse value from IMAP response

    :param val:
    :return:
    """
    if val in (b'NIL', b'nil') or not val:
        return None
    if val.isdigit():
        return int(val)
    return val


def literal_size(line: bytes) -> int:
    """Get length of transferred value

    :param line:
    :return: int
    """
    try:
        return int(line.strip(b'{}'))
    except ValueError as _:
        return int(line[line.rfind(b'{')+1:-1])


def get_part(line: bytes, default=None) -> bytes:
    """Get returned part name

    :param line:
    :param default:
    :return:
    """
    if b'[' not in line:
        return default
    return line[line.find(b'[')+1:line.find(b']')]


def get_transferred(line: bytes) -> bytes:
    """Get number of transferred data inside <>

    :param line:
    :return: bytes
    """
    if b'<' not in line:
        return None
    return line[line.find(b'<')+1:line.find(b'>')]


def check_literal(value: bytes, size: int):
    """Check if length of transferred data is equals to length reported by the
    server in literal size({0})

    Raises:
        ImapRuntimeError if real data length does not match with length
        reported by the server

    :param value: bytes
    :param size: int
    :param name: atom name
    :return value if length is correct
    """
    if size != len(value):
        msg = 'Expected {} but got {} . ' \
              'Value: {}'.format(size, len(value), value)
        raise ImapResponseParserError(msg)
    return value


class ResponseTokenizer(object):
    """Tokenize string into simple lexemes

    """

    __escaping_char = byte2int(b'\\')
    __quotes = set([byte2int(b'\''), byte2int(b'"')])
    __list_start = byte2int(b'(')
    __list_end = byte2int(b')')
    __space = byte2int(b' ')
    __square_bracket_start = byte2int(b'[')
    __square_bracket_end = byte2int(b']')

    __slots__ = ('__line', '__literals', '__len',
                 '__pos', '__cur_char', 'is_literal')

    def __init__(self, line, literals):
        self.parse_line(line, literals)

    def parse_line(self, line, literals):
        self.__line = line
        self.__literals = literals
        self.__len = len(line)
        self.__pos = 0
        self.__cur_char = b''

    def __get_literal(self, literal_str):
        return check_literal(self.__literals.pop(0), literal_size(literal_str))

    def __iter__(self):
        return self

    def __next__(self):

        if self.__pos >= self.__len:
            assert not self.__literals, 'Data left in literals' \
                                        ' {}'.format(self.__repr__())

            raise StopIteration

        self.__cur_char = self.__line[self.__pos]

        if self.__cur_char == self.__space:
            self.__pos += 1
            return self.__next__()

        if self.__cur_char in self.__quotes:
            self.__pos += 1
            return parse_value(self._read_until([self.__cur_char]))
        elif self.__cur_char == self.__list_start:
            self.__pos += 1
            return [i for i in self.__parse_list()]

        return parse_value(self.__read_util_space())

    def __parse_list(self):
        """Collects all next tokens into list

        :return: generator
        """
        if self.__line[self.__pos:self.__pos+1] == b')':
            self.__pos += 1
            return
        for item in self:
            yield item
            if self.__cur_char == self.__list_end:
                self.__cur_char = b''
                break
            if self.__line[self.__pos:self.__pos+1] == b')':
                self.__pos += 1
                break
        else:
            raise ImapResponseParserError(
                    'Could find closing ) in line '.format(self.__line)
            )

    def __read_util_space(self) -> bytes:
        """Reads until next whitespace occurs

        :return: bytes
        """
        return self._read_until(
                (self.__list_end, self.__space),
                self.__square_bracket_start,
                self.__square_bracket_end
        )

    def _read_until(self, looking_for, special_start=False,
                    special_end=False) -> bytes:
        """Reads until first specified char occurs

        :param looking_for: iterable
        :return: bytes
        """
        line = enumerate(self.__line[self.__pos:])
        special_count = 0
        for index, self.__cur_char in line:
            if self.__cur_char == self.__escaping_char:
                line.__next__()
                continue
            if self.__cur_char == special_start:
                special_count += 1
            if self.__cur_char == special_end:
                special_count -= 1
            if self.__cur_char not in looking_for or special_count > 0:
                continue
            return self.__get_value(self.__pos, self.__pos + index)
        else:
            if self.__space in looking_for:
                return self.__get_value(self.__pos, self.__len)

            raise ImapResponseParserError(
                    'Could not find {} in line {}'.format(
                            list(map(chr, looking_for)),
                            self.__line
                    )
            )

    def __get_value(self, start, end):
        value = self.__line[start:end]
        self.__pos = end + 1
        if value[-1:] == b'}':
            return self.__get_literal(value)
        return value

    def __repr__(self):
        return 'Line {}. Literal values {}'.format(self.__line,
                                                   self.__literals)


__ATOM_SPECIALS = set([byte2int(b'['), byte2int(b'<')])


def parse_atom_name(name: bytes):
    for index, char in enumerate(name):
        if char not in __ATOM_SPECIALS:
            continue
        truncated, rest = name[:index], name[index:]
        return truncated, {'part': get_part(rest),
                           'transferred': get_transferred(rest)}
    return name, {}