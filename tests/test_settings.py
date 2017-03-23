# -*- coding: utf-8 -*-
"""

"""
import os

from tests.base import BaseTestCase, sxmsettings


class Settings(BaseTestCase):

    def test_general(self):
        self.assertIsNotNone(sxmsettings.CONFIG)
        self.assertIsNotNone(sxmsettings.CONFIG.get('imap', 'port'))

    def test_config_from_file(self):
        self.reload_settings()
        self.assertIsNotNone(sxmsettings.CONFIG)
        self.assertEqual(sxmsettings.CONFIG.get('imap', 'port'), '143')

    def test_imap_settings(self):
        self.assertIsNotNone(sxmsettings.IMAP_CONFIG)
        for key in ['host', 'port', 'secure', 'keyfile', 'certfile']:
            self.assertIn(key, sxmsettings.IMAP_CONFIG)

    def test_imap_option_secure_boolean(self):
        self.assertIsInstance(sxmsettings.IMAP_CONFIG['secure'], bool)
