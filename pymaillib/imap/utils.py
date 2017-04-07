# -*- coding: utf-8 -*-
"""
    Imap4 Utils
    ~~~~~~~~~~~~~~~~
    Some helpers functions maybe you not need them but they are common
    and spread all over the IMAP module

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

import operator
from datetime import datetime
from email import policy
from email.header import decode_header as _email_decode_header
import collections
from email.parser import BytesParser, BytesHeaderParser
from typing import Any

import dateutil.parser

byte2int = operator.itemgetter(0)

END_OF_LIST_ORD = byte2int(b')')


def list_to_dict(items):
    """Create dictionary from a parenthesized list of attribute/value pairs

    :param items: list
    :return: dict
    """
    if not items:
        items = []

    # minimal
    #  dict(zip(items[0::2], items[1::2])
    def recursive(item):
        """Check value of parenthesized list and if it a sublist
        call list_to_dict recursively

        :param item:
        :return:
        """
        if is_iterable(item):
            return list_to_dict(item)
        return item

    return dict(zip(items[0::2], [recursive(item) for item in items[1::2]]))


def is_iterable(item):
    """Checks if variable is sequence excluding string and bytes

    :param item:
    :return: boolean
    """
    return isinstance(item, collections.Iterable) and not \
        isinstance(item, (bytes, str))


def build_content_part(main, subtype):
    """Helper function for BodyStructure entities.

    :param main: bytes
    :param subtype: bytes
    :return: bytes
    """
    return b'/'.join([main, subtype]).lower()


def linear_list(data):
    """Join multidimensional list (imaplib response) into linear list

    :param data:
    :return: generator
    """
    for item in iter(data):
        if is_iterable(item):
            yield from linear_list(item)
        else:
            yield item


def decode_parameter_value(value: bytes):
    """Decodes strings like '=?UTF-8?Q?' into human readable string

    :param value: bytes
    :return:
    """
    if not value:
        return ''

    if not isinstance(value, bytes):
        return value

    res = []
    for part, enc in _email_decode_header(value.decode()):
        if isinstance(part, bytes):
            if not enc:
                enc = 'utf-8'
            res.append(part.decode(enc, errors='replace'))
        else:
            res.append(part)
    return ''.join(res)


def build_imap_response_line(lines):
    """Build line from imaplib library

    :param lines: iterable
    :return: tuple bytes, list with literal values
    """
    lines = iter(lines)
    for line in lines:
        result = []
        literals = []
        while True:
            if is_iterable(line):
                line, literal = line
                literals.append(literal)
            result.append(line)
            if line[-1] == END_OF_LIST_ORD:
                break
            line = lines.__next__()
        yield b''.join(result), literals


def parse_datetime(value):
    """Parse date string from imap to datetime object

    :param value:
    :return:
    """

    if not value:
        return None
    return dateutil.parser.parse(value)


def parse_email(data: bytes) -> 'EmailMessage':
    """

    :param data: bytes
    :return: EmailMessage
    """
    return BytesParser(_class=EmailMessage, policy=policy.strict) \
        .parsebytes(data)


def parse_email_headers(data: bytes) -> 'EmailMessage':
    """

    :param data: bytes
    :return: EmailMessage
    """
    return BytesHeaderParser(_class=EmailMessage, policy=policy.default) \
        .parsebytes(data)


# import recursion
from .entity.email_message import EmailMessage


def escape_string(data: Any) -> str:
    """escapes string

    :param data:
    :return: str
    """
    if is_iterable(data):
        data = ' '.join([str(item) for item in data])
    return '"{}"'.format(data.replace('"', '\"'))


def get_date(value):
    """Returns date as string in format DD-Jun-YYYY

    :param value:
    :return:
    """
    if not value:
        return value
    if not isinstance(value, datetime):
        value = parse_datetime(value)
    return value.strftime("%d-%b-%Y")
