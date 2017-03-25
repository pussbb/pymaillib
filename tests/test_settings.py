# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

from tests.base import BaseTestCase


class Settings(BaseTestCase):

    def test_general(self):
        self.assertIsNotNone(self.config)
        self.assertIsNotNone(self.config.get('imap'))

    def test_imap_settings(self):
        for key in ['host', 'port', 'secure', 'keyfile', 'certfile']:
            self.assertIn(key, self.config.get('imap'))

    def test_imap_option_secure_boolean(self):
        self.assertIsInstance(self.config['imap']['secure'], bool)
