# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import os

from tests.base import BaseTestCase, mailsettings


class Settings(BaseTestCase):

    def test_general(self):
        self.assertIsNotNone(mailsettings.CONFIG)
        self.assertIsNotNone(mailsettings.CONFIG.get('imap', 'port'))

    def test_config_from_file(self):
        self.reload_settings()
        self.assertIsNotNone(mailsettings.CONFIG)
        self.assertEqual(mailsettings.CONFIG.get('imap', 'port'), '143')

    def test_imap_settings(self):
        self.assertIsNotNone(mailsettings.IMAP_CONFIG)
        for key in ['host', 'port', 'secure', 'keyfile', 'certfile']:
            self.assertIn(key, mailsettings.IMAP_CONFIG)

    def test_imap_option_secure_boolean(self):
        self.assertIsInstance(mailsettings.IMAP_CONFIG['secure'], bool)
