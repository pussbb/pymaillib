# -*- coding: utf-8 -*-
"""
    Imap Envelope Entity
    ~~~~~~~~~~~~~~~~
    Imap Envelope Entity

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from typing import Iterator, List

from ..utils import decode_parameter_value, parse_datetime
from . import ImapEntity, SlotBasedImapEntity


class Envelope(SlotBasedImapEntity):
    """Represents IMAP ENVELOPE

    """
    __slots__ = ('date', 'subject', 'from_', 'sender', 'reply_to', 'to', 'cc',
                 'bcc', 'in_reply_to', 'message_id')

    @staticmethod
    def from_list(items: list) -> 'Envelope':
        """Construct Envelope object from a list

        :param items: list
        :return:
        """

        date, subj, *addrs, in_reply, msg_id = items
        return Envelope(
            parse_datetime(date),
            decode_parameter_value(subj),
            *[AddressList.from_list(addr) for addr in addrs],
            in_reply_to=in_reply,
            message_id=msg_id
        )


class Address(SlotBasedImapEntity):
    """Represents email address in ENVELOPE

    """

    __slots__ = 'name', 'route', 'mailbox', 'host'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = decode_parameter_value(self.name)


class AddressList(ImapEntity):
    """Address list for an envelope response

    """

    __slots__ = '_addresses',

    def __init__(self, addresses: List[Address]):
        self._addresses = addresses

    @staticmethod
    def from_list(items) -> 'AddressList':
        """Convert list into AddresList object with Address objects

        :param items: iterable
        :return:
        """
        if not items:
            return AddressList([])
        return AddressList([Address(*item) for item in items])

    def __iter__(self) -> Iterator[Address]:
        yield from self._addresses

    def dump(self) -> List[Address]:
        """Serialize class attributes

        :return:
        """
        return self._addresses
