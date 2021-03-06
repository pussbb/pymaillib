# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib
from email.headerregistry import Address

from pymaillib.imap.entity.email_message import EmailMessage
from pymaillib.imap.query.builders.search import SearchQueryBuilder
from pymaillib.imap.query.builders.fetch import FetchQueryBuilder
from pymaillib.imap.query.builders.store import StoreQueryBuilder
from pymaillib.imap.client import ImapClient
from pymaillib.imap.commands import ImapBaseCommand
from pymaillib.imap.entity.folder import ImapFolder
from pymaillib.imap.entity.server import Namespaces
from pymaillib.imap.exceptions.base import ImapIllegalStateException, \
    ImapObjectNotFound, ImapClientError, ImapRuntimeError
from pymaillib.imap.exceptions.rfc5530 import ImapAlreadyExists
from pymaillib.user import UserCredentials
from tests.base import BaseTestCase

imaplib.Debug = 0


class Imap(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.imap = ImapClient(self.config.get('imap'),
                               UserCredentials('sxadmin', '1'))

    def test_init_imap_client(self):
        with self.assertRaises(TypeError):
            ImapClient()

    def test_imap_connection_opened(self):
        self.assertTrue(self.imap.opened)

    def test_capabilities(self):
        self.assertIn('IMAP4REV1', self.imap.capabilities)
        self.assertTrue(self.imap.supports('NooP'))
        self.assertFalse(self.imap.supports('SomeOtherThing'))

    def test_imap_context(self):
        with self.assertRaises(ImapIllegalStateException):
            list(self.imap.folders())

    def test_folder_list(self):
        with self.imap as client:
            folders = list(client.folders())
            self.assertGreater(len(folders), 0)
            for folder in client.folders():
                self.assertIsNotNone(folder.direct_ref)

    def test_imap_folder_by_name(self):
        with self.imap as client:
            self.assertRaises(ImapObjectNotFound, client.folder_by_name,
                              'non existing folder')

        with self.imap as client:
            self.assertIsNotNone(client.folder_by_name('INBOX'))

    def test_imap_folder_manipulations(self):
        folder_name = 'test ывавы & &  " '
        renamed_folder_name = 'INBOX/renamed'
        with self.imap as client:
            if client.folder_exists(folder_name):
                client.delete_folder(client.folder_by_name(folder_name))

            folder = client.create_folder(folder_name)
            if client.folder_exists(renamed_folder_name):
                client.delete_folder(client.folder_by_name(renamed_folder_name))

            renamed = client.rename_folder(
                folder,
                'renamed',
                client.folder_by_name('INBOX')
            )
            client.delete_folder(renamed)

    def test_parse_folder(self):
        #  I have not seen such response and it not by rfc
        #  (b'  "/" "Other Users"', '/', 'Other Users'),
        lines = [
            (b'(\\X-SpecialFolder=SentItems \\X-DirectRef=00011a035dc33e08 '
             b'\\X-ModDate=20151029071158 \\X-Total-Msgs=2 \\X-Unseen-Msgs=0) '
             b'"/" "Sent Items"', '/', 'Sent Items'),
            (b'(\X-DirectRef=00011a0054a8e393 \X-ModDate=20151029140200 '
             b'\X-Total-Msgs=0 \X-Unseen-Msgs=0) "/" INBOX', '/', 'INBOX'),
            (b'(\\NoSelect) "/rrer/ere" "Other Users"', '/rrer/ere', 'Other Users'),
            (b'(\\NoSelect) \'/\' "Other Users"', '/', 'Other Users'),
            (b'() "/" "Other Users"', '/', 'Other Users'),
            (b'(\NoSelect) "/" 17.03.2002', '/', '17.03.2002'),
            (b'(\NoInferiors \Marked) "/" in', '/', 'in'),
            (b'(\NoInferiors \UnMarked) "/" todays-junk', '/', 'todays-junk'),
            (b'(\HasNoChildren) "/" "Travel"', '/', 'Travel'),
            (b'(\Noselect \HasChildren) "/" "[Gmail]"', '/', '[Gmail]'),
            (b'(\Noinferiors \HasNoChildren) "." INBOX', '.', 'INBOX'),
            (b'(\HasNoChildren \Archive) "." Archive', '.', 'Archive'),
            (b'(\HasNoChildren \Drafts) "." Drafts', '.', 'Drafts'),
            (b'(\HasNoChildren \Junk) "." "Junk Mail"', '.', 'Junk Mail'),
            (b'(\HasNoChildren \Sent) "." "Sent Items"', '.', 'Sent Items'),
            (b'(\HasNoChildren \Trash) "." Trash', '.', 'Trash'),
        ]

        for line in lines:
            raw, path, name = line
            folder = ImapFolder.build(raw)
            self.assertEqual(folder.name, name)
            self.assertEqual(folder.delimiter, path)
            self.assertIsNotNone(folder.direct_ref)

        with self.assertRaises(ImapRuntimeError) as exp:
            ImapFolder.build(b'  "/" "Other Users"')

        self.assertIn('not enough values to unpack', str(exp.exception))

    def test_check_response(self):
        imap_cmd = ImapBaseCommand()
        with self.assertRaises(ImapAlreadyExists):
            imap_cmd.check_response(
                    'NO',
                    ['NO [ALREADYEXISTS] Mailbox "that" already exists',
                     b'[ALREADYEXISTS] Mailbox "that" already exists']
            )

        with self.assertRaises(ImapClientError):
            imap_cmd.check_response(
                    'NO',
                    ['NO FETCH invalid message set',
                     b'FETCH invalid message set']
            )

    def test_fetch(self):
        with self.imap as client:
            client.select_folder(client.folder_by_name('INBOX'))
            msgs = client.fetch(FetchQueryBuilder.all(1))
            self.assertTrue(msgs)

    def test_namespaces(self):
        with self.imap as client:
            namespaces = client.namespace()
            self.assertIsNotNone(namespaces)
            self.assertIsInstance(namespaces, Namespaces)

    def test_proxy_function(self):
        with self.imap as client:
            self.assertIsNotNone(client.recent())

    def test_store(self):
        folder = ImapFolder(b'Inbox', b'/', {})
        query = StoreQueryBuilder(1)
        query.remove(r'\SEEN')
        with self.imap as client:
            client.select_folder(folder)
            res = list(client.store(query))
            self.assertIsNotNone(res)
            self.assertEqual(len(res), 1)

    def test_search(self):
        folder = ImapFolder(b'Inbox', b'/', {})
        query = SearchQueryBuilder()
        query.seen()
        with self.imap as client:
            client.select_folder(folder)
            res = list(client.search(query))
            self.assertIsNotNone(res)
            self.assertGreater(len(res), 1)

    def test_message_manipulation(self):
        msg = EmailMessage()
        msg['Subject'] = "Ayons asperges pour le déjeuner"
        msg['From'] = Address("Pepé Le Pew", "pepe", "example.com")
        msg['To'] = (Address("Penelope Pussycat", "penelope", "example.com"),
                     Address("Fabrette Pussycat", "fabrette", "example.com"))
        msg.set_content("""\
        Salut!

        Cela ressemble à un excellent recipie[1] déjeuner.

        [1] http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718

        --Pepé
        """)
        folder = ImapFolder(b'Inbox', b'/', {})
        with self.imap as client:
            client.select_folder(folder)
            msg = client.append_message(msg, folder)
            self.assertIsNotNone(msg)
            self.assertIsInstance(msg, EmailMessage)
            self.assertIsNotNone(msg.uid)
            # update message
            msg.replace_header('Subject', 'Renamed')
            old_uid = msg.uid
            client.update_message(msg, folder)
            self.assertIsNotNone(msg)
            self.assertIsInstance(msg, EmailMessage)
            self.assertIsNotNone(msg.uid)
            self.assertNotEqual(old_uid, msg.uid)
            client.delete_message(msg)
