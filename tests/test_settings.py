# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import os

from tests.base import BaseTestCase, mailsettings


class Settings(BaseTestCase):

    def test_general(self):
        self.assertIsNotNone(self.config)
        self.assertIsNotNone(self.config.get('imap'))

    def test_imap_settings(self):
        for key in ['host', 'port', 'secure', 'keyfile', 'certfile']:
            self.assertIn(key, self.config.get('imap'))

    def test_imap_option_secure_boolean(self):
        self.assertIsInstance(self.config['imap']['secure'], bool)

    def test_config_from_env(self):

        with self.assertRaises(RuntimeError) as excp:
            mailsettings.Config().from_envvar('ddd')
        self.assertIn('Environment key', str(excp.exception))

        os.environ['PYMAILLIB_CONFIG'] = ''
        with self.assertRaises(RuntimeError) as excp:
            mailsettings.Config().from_envvar('PYMAILLIB_CONFIG')
        self.assertIn('Environment key', str(excp.exception))

        os.environ['PYMAILLIB_CONFIG'] = './pymaisssl.ini'
        with self.assertRaises(RuntimeError) as excp:
            mailsettings.Config().from_envvar('PYMAILLIB_CONFIG')
        self.assertIn('does not exists', str(excp.exception))
