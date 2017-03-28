# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

from pymaillib.mailbox import UserMailbox
from pymaillib.user import UserCredentials
from tests.base import BaseTestCase


class UserMailboxTest(BaseTestCase):

    def test_init_user_mailbox(self):
        with self.assertRaises(TypeError):
            UserMailbox(config=self.config)
        with self.assertRaises(AssertionError):
            UserMailbox('', '', config=self.config)

    def test_auth_data(self):
        self.assertIsInstance(UserMailbox('a', 'a', self.config).auth_data,
                              UserCredentials)

    def test_check_auth(self):
        self.assertTrue(UserMailbox('a', 'a', self.config).check(
            UserCredentials('a', 'a')))
        self.assertFalse(
            UserMailbox('a', 'a', self.config).check(UserCredentials('a', '2a'))
        )

    def test_close(self):
        self.assertFalse(UserMailbox('a', 'a', self.config).close())

    def test_repr_user_mailbox(self):
        self.assertIn('user@', str(UserMailbox('user@mm.com', '2', self.config)))
