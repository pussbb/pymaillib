# -*- coding: utf-8 -*-
"""
    Imap Email Message
    ~~~~~~~~~~~~~~~~
    Imap Email Message

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from email import policy

from email.parser import BytesParser

from . import ImapEntity


class ImapFetchedItem(dict):

    def __setitem__(self, key, value):
        if key == 'BODY':
            value = {**value, **super().get(key, {})}
        super().__setitem__(key, value)


class ImapEmailMessage(ImapEntity):

    def __init__(self, uid, seq=None, **kwargs):
        self.__uid = uid
        self.__seq = seq
        self.__data = kwargs
        self.__email = None
        self.__rfc822 = None
        self.__rfc822_text = None
        self.__rfc822_header = None
        self.update()

    def update(self):

        rfc_header = self.__data.pop('RFC822.HEADER', b'')
        rfc_text = self.__data.pop('RFC822.TEXT', b'')

        if rfc_header and rfc_text:
            self.__rfc822 = self.__parse_email(rfc_header+rfc_text)
        if 'RFC822' in self.__data:
            self.__rfc822 = self.__parse_email(self.__data.get('RFC822', b''))

        self.__rfc822_text = self.__parse_email(rfc_text)
        self.__rfc822_header = self.__parse_email(rfc_header)

        if 'BODY' not in self.__data:
            return

        self.__email = self.__parse_email(self.__data['BODY'].pop(0, b''))
        body_structure = self.__data.get('BODYSTRUCTURE', b'')
        if body_structure and 'BODYSTRUCTURE' not in self.__data:
            self.__data['BODYSTRUCTURE'] = body_structure

        header = self.__parse_email(self.__data['BODY'].pop('HEADER', b''))
        if header:
            self.__rfc822_header = header

    def __parse_email(self, data):
        if not data:
            return None
        return BytesParser(policy=policy.default).parsebytes(data)

    def __getattr__(self, item):
        return self.__data[item.upper()]

    @property
    def uid(self):
        return self.__uid

    @property
    def sequence_id(self):
        return self.__seq

    @property
    def internal_date(self):
        return self.__data.get('INTERNALDATE')

    @property
    def body_structure(self):
        return self.__data.get('BODYSTRUCTURE')

    @property
    def envelope(self):
        return self.__data.get('ENVELOPE')

    @property
    def rfc822(self):
        return self.__rfc822

    @property
    def rfc822_header(self):
        return self.__rfc822_text

    @property
    def rfc822_text(self):
        return self.__rfc822_header

    @property
    def flags(self):
        return self.__data.get('FLAGS', [])

    @property
    def size(self):
        return self.rfc822_size

    @property
    def rfc822_size(self):
        return self.__data.get('RFC822.SIZE')

    @property
    def email_message(self):
        if self.rfc822:
            return self.rfc822
        return self.__email

    def dump(self):
        yield from {
            'uid': self.uid,
            'seq': self.sequence_id,
            'internal_date': self.internal_date,
        }

    def __repr__(self):
        return "{}".format(self.dump())

    @staticmethod
    def from_dict(items):
        try:
            return ImapEmailMessage(items.pop('UID'), items.pop('SEQ'), **items)
        except KeyError as _:
            print(items)
            raise
