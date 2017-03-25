# -*- coding: utf-8 -*-
"""
    Imap4 Commands
    ~~~~~~~~~~~~~~~~
    Imap4 Commands packages contains list of all supported imap4 commands

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib
from traceback import print_exc

from ..parsers import ResponseTokenizer, get_part
from ..utils import list_to_dict
from ..constants import IMAP4_OK_RESULT
from ..exceptions import ImapRuntimeError, RFC5530, ImapClientError


class ImapBaseCommand(object):
    """Base class for all IMAP commands each ImapCommand should be a subclass
     of this class

    Attributes:
        _COMMAND defines IMAP command name
    """

    _COMMAND = None

    @property
    def name(self) -> str:
        """Returns IMAP command name if _COMMAND is not set ImapRuntimeError
        is raised
        :return: AnyStr
        """
        assert self._COMMAND, ImapRuntimeError('Command name can not be empty')
        return self._COMMAND

    def run(self, imap_obj: imaplib.IMAP4):
        """Abstract function child classes should implement it

        :param imap_obj: imaplib.IMAP4
        """
        raise NotImplemented

    def error_message(self):
        """Specifies default error message for command

        :return:
        """
        return ''

    def exception_class(self):
        """Specifies default exception class for command

        :return: class of
        """
        return ImapClientError

    def tagged_message(self, data: list) -> bytes:
        """returns message string from server tagged response

        :param data:
        :return:
        """
        msg = data[-1]
        if not msg:
            msg = b''
        return msg

    def check_response(self, status, data):
        """Checks if requested command successfully executed

        Raises:
            - ImapClientException if error occurred

        :param status: string OK, BAD ....
        :param data: tagged response from imaplib
        :return:
        """
        if status == IMAP4_OK_RESULT:
            return data

        match = get_part(self.tagged_message(data), b'')
        cls = RFC5530.get(match.decode(), self.exception_class())
        raise cls("{} {}".format(self.error_message(), data))

    def untagged_value(self, imap_obj: imaplib.IMAP4, tag: str,
                       fallback=None):
        """Gets value for untagged key and decodes it into bytes

        :param imap_obj:  imaplib.IMAP4
        :param tag: key of untagged response
        :param fallback: default value if key does not exists in IMAP response
        :return: bytes
        """
        try:
            val = imap_obj.response(tag)[1][0]
            # we need bytes python3 require bytes for strip .....
            # but we got an str
            # TypeError: a bytes-like object is required, not 'str'
            if val:
                if val == 'NIL':
                    return fallback
                val = val
            else:
                val = fallback
            return val
        except IndexError as _:
            print_exc()
        return fallback

    def parse_string_pair(self, data: bytes) -> dict:
        """Parses string key pairs returned by IMAP server. For e.g.
        ``` ("name" "imap4dv1" "version" "12.5.6.6666" ... )``` and returns
        as dictionary

        :param data: bytes
        :return: dict
        """
        if not data or data == 'NIL':
            return {}
        return list_to_dict(list(ResponseTokenizer(data, [])))

    def __repr__(self):
        return '{} {}'.format(self.name, self.__class__)
