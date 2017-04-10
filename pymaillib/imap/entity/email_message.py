# -*- coding: utf-8 -*-
"""
    Imap Email Message
    ~~~~~~~~~~~~~~~~
    Imap Email Message

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import quopri
import uu
from email import policy
from email._encoded_words import decode_b
from email.errors import InvalidBase64CharactersDefect
from email.message import EmailMessage as ImapLibEmailMessage, MIMEPart
from email.base64mime import body_decode

from io import BytesIO
from typing import Any, List, AnyStr, Generator

from ..exceptions import ImapRuntimeError
from . import ImapEntity


class EmailMessage(ImapLibEmailMessage, ImapEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__uid = 0
        self.__sequence = 0

    @property
    def uid(self) -> int:
        """Message UID
        
        :return: 
        """
        return self.__uid

    @uid.setter
    def uid(self, value: int):
        """Set message uid
        
        :param value: int
        :return: 
        """
        self.__uid = value

    @property
    def sequence(self) -> int:
        """Sequence number
        
        :return: int
        """
        return self.__sequence

    @sequence.setter
    def sequence(self, value: int):
        """Set sequence number
        
        :param value: 
        :return: 
        """
        self.__sequence = value

    def headers(self) -> List[AnyStr]:
        """Email message headers if present
        
        :return: 
        """
        return self._headers

    def get_content(self) -> AnyStr:
        try:
            return super().get_content()
        except InvalidBase64CharactersDefect as _:
            return self.__parse_linear_base64()

    def __parse_linear_base64(self) -> bytes:
        """Original parser will fail in case such email
        ```
        Content-Type: text/plain\r\n
        Content-Transfer-Encoding: base64\r\n\r\n
        PHByZW...==\r\n
        ...
        ...==\r\n
        ```
        as a workaround getting raw body and split by '\n' and parse xml
        as string list
        """
        # splitlines does not work and I don't know why . so lets just manually
        # split string by '\n' delimiter
        return b'\n'.join([body_decode(line)
                           for line in self.__message.get_payload()])

    def __repr__(self):
        return self.as_string()

    def dump(self) -> bytes:
        """Returns email as bytes
        
        :return: 
        """
        return self.as_bytes()


class ImapFetchedItem(dict, ImapEntity):
    """Generic class for fetched item from imap
    
    """

    def __init__(self, seq=None, **kwargs):
        if not seq:
            super().__init__(**kwargs)
        for key, value in seq:
            self[key] = value

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            for item in list(value.keys()):
                if isinstance(item, int):
                    if item == 0:
                        value[item] = parse_email(value[item])
                    continue
                if 'BODYSTRUCTURE' in value:
                    super().__setitem__('BODYSTRUCTURE',
                                        value.pop('BODYSTRUCTURE'))
                if 'HEADER' == value:
                    self.__proccess_header(value.pop('HEADER'))
                if 'HEADER.FIELDS' in item:
                    self.__proccess_header(value.pop(item))

            super().__setitem__(key, {**super().get(key, {}), **value})
        elif 'RFC822.HEADER' == key:
            self.__proccess_header(value)
        elif 'RFC822' == key:
            super().__setitem__(key, parse_email(value))
        else:
            super().__setitem__(key, value)

    def __proccess_header(self, data: bytes):
        """Parsers email header 
        
        :param data: bytes 
        :return: 
        """
        if 'HEADER' not in self:
            super().__setitem__('HEADER', parse_email_headers(data))
            return
        for key, name in parse_email_headers(data).headers():
            try:
                self['HEADER'].replace_header(key, name)
            except KeyError as _:
                self['HEADER'].add_header(key, name)

    def __getattr__(self, item):
        return self.get(item.upper().replace('_', '.'), self.get(item))

    def header_item(self, key: AnyStr, default=None):
        """Get header item value
        
        :param key: name of header item
        :param default: 
        :return: 
        """
        store = {key: default}
        if 'HEADER' in self:
            store = self['HEADER']
        else:
            email = self.email_message
            if email:
                store = email
        return store[key]

    @property
    def email_message(self) -> EmailMessage:
        """Returns EmailMessage object 
        
        :return: 
        """
        return self.get('RFC822', self.get_fetched_part(0))

    def get_fetched_part(self, num: Any):
        """
        
        :param num: 
        :return: 
        """
        try:
            num = int(num)
        except ValueError as _:
            pass
        return self.get('BODY', {}).get(num)

    def get_fetched_mime_part(self, num):
        """
        
        :return: 
        """
        part_data = self.get_fetched_part(num)
        if not self.bodystructure:
            raise ImapRuntimeError('You forgot to load bodystructure')
        part_info = self.bodystructure.find_by_mime_id(str(num))

        if not part_info:
            raise ImapRuntimeError('Could not find part info')

        """
        part = EmailMessage(policy.strict)
        part.set_charset(part_info.charset)
        if part_info.is_multipart():
            part.set_boundary(part_info.boundary)
        part.set_default_type(part_info.content_part)
        part.set_type(part_info.content_part)
        # <'bytes'>, maintype, subtype, cte="base64", disposition=None,

        part.set_content(part_data, maintype=part_info.main_type, subtype=part_info.subtype, cte=part_info.encoding)
        print(part['content-transfer-encoding'])
        #print(decode_b(part_data))
        print(part.get_content())
        """

        return part_info, part_data

    def decode(self, part_info, data):
        if part_info.encoding == 'quoted-printable':
            return quopri.decodestring(data)
        elif part_info.encoding == 'base64':
            # XXX: this is a bit of a hack; decode_b should probably be factored
            # out somewhere, but I haven't figured out where yet.
            value, defects = decode_b(b''.join(data.splitlines()))
            return value
        elif part_info.encoding in ('x-uuencode', 'uuencode', 'uue', 'x-uue'):
            in_file = BytesIO(data)
            out_file = BytesIO()
            try:
                uu.decode(in_file, out_file, quiet=True)
                return out_file.getvalue()
            except uu.Error:
                # Some decoding problem
                return data

    def dump(self) -> Generator[Any, Any, Any]:
        """
        
        :return: 
        """
        for item, value in self.items():
            if 'HEADER' == item:
                yield item, dict(value.headers())
            elif 'BODY' == item:
                yield item, dict(self.__walk_fetched_body_parts(value))
            else:
                yield item, value

    def __walk_fetched_body_parts(self, data):
        for key, value in data.items():
            if isinstance(value, EmailMessage):
                yield key, value.as_bytes()
            yield key, value

    def __repr__(self):
        return "{}".format(self.dump())


from ..utils import parse_email_headers, parse_email
