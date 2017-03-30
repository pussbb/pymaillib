# -*- coding: utf-8 -*-
"""
    Imap Folder Entity
    ~~~~~~~~~~~~~~~~
    Imap4 Folder

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import uuid

from ..parsers import ResponseTokenizer
from ..constants import IMAP4_FOLDER_SPECIAL_CHARS
from ..utf7 import imap4_utf7_decode, imap4_utf7_encode
from ..exceptions import ImapRuntimeError
from . import ImapEntity


class ImapFolder(ImapEntity):
    """Represents imap folder attributes

    """

    def __init__(self, name: str, path: str, attributes: dict):
        assert name, ImapRuntimeError('Folder name can not be emtpy')
        assert path, ImapRuntimeError('Folder path can not be emtpy')
        self.__name = name
        #  hierarchy delimiter
        self.__delimiter = path
        self.__attributes = attributes
        self.__stats = {}

    @property
    def name(self):
        """Folder name

        :return: bytes
        """
        return self.__name

    @property
    def delimiter(self) -> str:
        """ Hierarchy delimiter at IMAP Server

        :return:
        """
        return self.__delimiter

    def parent(self):
        """returns instance of ImapFolder wirh parent path

        """
        name = ''.join(self.name.split(self.delimiter)[:-1])
        if not name:
            return None
        return ImapFolder(name, self.delimiter, {})

    @property
    def direct_ref(self) -> str:
        """  some folders does not have dref 'Other Users' , 'Public Folders'
        they have 'NoSelect' attribute

        :return:
        """
        return self.__attributes.get(
            b'X-DirectRef',
            uuid.uuid5(uuid.NAMESPACE_URL, self.name).hex
        )

    @property
    def folder_class(self):
        """Scalix attribute

        :return:
        """
        return self.__attributes.get(b'X-FolderClass', None)

    @property
    def special_folder(self):
        """Scalix attribute

        :return:
        """
        attr = self.__attributes.get(b'X-SpecialFolder', None)
        return attr or self.name == 'INBOX'

    @property
    def selectable(self):
        """Indicates is folder selectable or not. If folder is not selectable
        any other request to imap server to this folder will fail.

        :return:
        """
        return b'Noselect' not in self.__attributes

    @property
    def stats(self):
        return self.__stats

    @stats.setter
    def stats(self, data: dict):
        self.__stats = data

    @property
    def unseen(self):
        """Number of new messages

        :return:
        """
        return self.__stats.get(
            'UNSEEN',
            int(self.__attributes.get(b'X-Unseen-Msgs', 0))
        )

    @property
    def modified(self):
        """Scalix attribute. Folder last modification time

        :return:
        """
        return self.__attributes.get(b'X-ModDate')

    @property
    def total(self):
        """Amount of existing messages in mailbox

        :return:
        """
        return self.__stats.get(
            'EXISTS',
            int(self.__attributes.get(b'X-Total-Msgs', 0))
        )

    def __repr__(self):
        return 'Name:{0} Path: {1} Attributes:{2} Stats {3}'.format(
            self.name,
            self.delimiter,
            self.__attributes,
            self.__stats
        )

    @property
    def editable(self):
        """Indicates can rename or delete folder

        :return:
        """
        return not self.special_folder and self.selectable

    def imap_name(self):
        """returns escaped printable folder name

        :return:
        """
        return ImapFolder.escape_name(imap4_utf7_encode(self.name))

    def dump(self):
        """for json render

        :return: dict
        """
        return {
            'name': self.name,
            'delimiter': self.delimiter,
            'total': self.total,
            'unread': self.unseen,
            'dref': self.direct_ref,
            'modified': self.modified,
            'class': self.folder_class,
            'special_folder': self.special_folder,
            'stats': self.__stats,
            'editable': self.editable
        }

    @staticmethod
    def build(data: bytes) -> object:
        """Construct from raw string valid ImapFolder object

        :param data:
        :return: ImapFolder object
        """

        try:
            raw_attributes, path, name = list(ResponseTokenizer(data, []))
        except Exception as exp:
            raise ImapRuntimeError(b'Could not parse line: ' + data, exp)

        attributes = {}
        for attr in raw_attributes:
            attr_name, _, value = attr.partition(b'=')
            attributes[attr_name] = value

        return ImapFolder(name, imap4_utf7_decode(path), attributes)

    @staticmethod
    def escape_name(name) -> str:
        """Escapes specials chars decodes to imap utf7 encoding

        :param name:
        :return:
        """
        name = imap4_utf7_encode(name)
        if IMAP4_FOLDER_SPECIAL_CHARS.findall(name):
            return b'"' + name.replace(b'"', b'\"') + b'"'
        return name

    @staticmethod
    def build_folder_name(name: str, parent=None):
        """Builds new folder name used in CREATE RENAME imap command classes

        :param name: bytes or str
        :param parent: ImapFolder
        """
        root = ''
        if parent:
            root = ''.join([parent.name + parent.delimiter])
        return ImapFolder.escape_name(''.join([root, name]))
