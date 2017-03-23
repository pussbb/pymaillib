# -*- coding: utf-8 -*-
"""
    Imap BodyStructure Entity
    ~~~~~~~~~~~~~~~~
    Imap BodyStructure Entity

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

from ..utils import build_content_part, list_to_dict, decode_parameter_value, \
    is_iterable
from .envelope import Envelope
from . import ImapEntity, SlotBasedImapEntity

""" NOTES
Some messaging systems provide different subtypes of Multiparts. For example,
MIME specifies a set of subtypes that include "alternative", "mixed", "related",
"parallel", "signed", etc.

"""


class SimpleBodyPart(SlotBasedImapEntity):
    """Class to represent simple body part

    """
    __slots__ = ('main_type', 'subtype', 'attributes', 'part_id',
                 'description', 'encoding', 'size', 'charset', 'part_id',
                 'text_size', 'md5', 'disposition', 'language', 'location',
                 'name', 'filename', 'mime_id', 'content_part')

    def __init__(self, *args, mime_id=None):
        """Init main message attributes

        :param args: tuple
        :param mime_id:
        :return:
        """
        args, _ = self._bulk_append(self.__rfc_default_fields(), list(args), {})

        self.attributes = list_to_dict(self.attributes)

        self.content_part = build_content_part(self.main_type, self.subtype)
        self.charset = self.attributes.pop(b'charset', None)
        self.name = decode_parameter_value(self.attributes.pop(b'name', None))

        self.mime_id = mime_id
        self.filename = None
        self.md5 = None
        self._init_rest(*args)

    def __rfc_default_fields(self):
        return ('main_type', 'subtype', 'attributes', 'part_id', 'description',
                'encoding', 'size')

    def _init_rest(self, text_size=None, md5_or_list=None, disposition=None,
                   language=None, location=None):
        """Try to create rest attributes of message part

        :param text_size:
        :param md5_or_list:
        :param disposition:
        :param language:
        :param location:
        :return:
        """
        self.text_size = text_size
        if not is_iterable(md5_or_list):
            self.md5 = md5_or_list
        else:
            value = list_to_dict(md5_or_list)
            if value.get(b'attachment'):
                self.filename = decode_parameter_value(
                        value[b'attachment'].pop(b'filename', None)
                )
            self.attributes = {**self.attributes, **value}
        self.disposition = list_to_dict(disposition)
        self.language = language
        self.location = location


class MessageRFC822BodPart(SimpleBodyPart):
    """Represent MESSAGE/RFC822 message body part and his attributes

    """

    __slots__ = ('envelope', 'bodystructure', 'line_count')

    def _init_rest(self, envelope, bodystructure, line_count, *args):
        """Init MESSAGE/RFC822 specific attributes then rest all possible

        :param envelope:
        :param bodystructure:
        :param line_count:
        :param args:
        :return:
        """
        self.envelope = Envelope.from_list(envelope)
        self.bodystructure = BodyStructure.build(bodystructure, self.mime_id,
                                                 True)
        self.line_count = line_count
        super()._init_rest(*args)


class MultiPartBodyPart(SimpleBodyPart):
    """Represent Multipart container

    """

    __slots__ = ('main_type', 'subtype', 'boundary', 'attributes',
                 'disposition', 'language', 'location', 'content_part',
                 'mime_id', '_parts')

    def __init__(self, subtype: bytes, attributes=None, disposition=None,
                 language=None, location=None, mime_id=None, parts=None):
        self.main_type = b'multipart'
        self.subtype = subtype
        self.attributes = list_to_dict(attributes)
        self.boundary = self.attributes.pop(b'boundary', None)
        self.disposition = disposition
        self.language = language
        self.location = location
        self.content_part = build_content_part(self.main_type, subtype)
        self.mime_id = mime_id
        self._parts = parts

    @property
    def parts(self) -> list:
        return self._parts

    def __iter__(self):
        yield self
        for item in self._parts:
            try:
                yield from item
            except TypeError as _:
                yield item


class BodyStructure(ImapEntity):
    """Generic class to hold all bady parts in one place with some additional
    functionality

    """

    __slots__ = ('__part')

    def __init__(self, part):
        self.__part = part

    def is_multipart(self):
        return isinstance(self.__part, MultiPartBodyPart)

    @property
    def part(self) -> SimpleBodyPart:
        """Returns main part of the message

        :return: object
        """
        return self.__part

    def __iter__(self):
        try:
            yield from self.__part
        except TypeError as _:
            yield self.__part

    def dump(self):
        """Printable version

        :return: list
        """
        yield from self

    def find_by_mime_id(self, mime_id):
        """Searchers message part by his positional index

        :param mime_id: str
        :return:
        """
        for item in self:
            if item.mime_id == mime_id:
                return item

    def __repr__(self):
        return '{}'.format([item.dump() for item in self.dump()])

    @staticmethod
    def build(items, index=0, recursive=False):
        """Constructs instance of BodyStructure class with all message parts
        from a list

        :param items: list
        :param index: int or str
        :param recursive: boolean
        :return:
        """
        def walk(arg, index_, recursive_):
            """Walk throw message parts

            :param arg:
            :param index_: int or str
            :param recursive_: boolean
            :return:
            """
            if is_iterable(arg[0]):
                parts = []
                for pos, item in enumerate(arg):
                    if not is_iterable(item):
                        arg = arg[pos:]
                        break
                    mime_id = '{}.{}'.format(index_, pos + 1)
                    if not recursive_:
                        mime_id = pos + 1
                    parts.append(walk(item, mime_id, True))
                part = MultiPartBodyPart(*arg, mime_id=index_, parts=parts)
            else:
                #  simple message
                if index_ == 0 and not recursive_:
                    index_ = 1
                if arg[1].lower() == b'rfc822':
                    part = MessageRFC822BodPart(*arg, mime_id=index_)
                else:
                    part = SimpleBodyPart(*arg, mime_id=index_)
            return part

        return BodyStructure(walk(items, index, recursive))
