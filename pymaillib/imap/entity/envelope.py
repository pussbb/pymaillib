# -*- coding: utf-8 -*-
"""
    Imap Envelope Entity
    ~~~~~~~~~~~~~~~~
    Imap Envelope Entity

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from typing import Iterator, List
from email.headerregistry import Address as HeaderAddress

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


class Address(SlotBasedImapEntity, HeaderAddress):
    """Represents email address in ENVELOPE

    """

    __slots__ = 'name', 'route', 'mailbox', 'host', '_display_name', \
                '_username', '_domain'

    def __init__(self, *args, **kwargs):
        args += (None,)*3
        super().__init__(*args, **kwargs)
        if self.name:
            self._display_name = self.name.decode()
        else:
            self._display_name = ''
        self.name = decode_parameter_value(self.name)
        self._username = self.mailbox.decode()
        self._domain = self.host.decode()

    @property
    def rfc(self) -> str:
        """Get formatted address with display name and email
        
        :return: 
        """
        return '{} <{}@{}>'.format(self.display_name, self.username,
                                   self.domain).strip()

    def dump(self) -> dict:
        """
        
        :return: 
        """
        return {
            'name': self.name,
            'route': self.route,
            'mailbox': self.mailbox,
            'host': self.host,
            'addr_spec': self.addr_spec,
            'display': self.rfc,
        }


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
