# -*- coding: utf-8 -*-
"""

"""
import unittest

from pymaillib import UserMailbox
from pymaillib.user import UserCredentials


class UserMailboxTest(unittest.TestCase):

    def test_init_user_mailbox(self):
        with self.assertRaises(TypeError):
            UserMailbox()
        with self.assertRaises(AssertionError):
            UserMailbox('', '')

    def test_auth_data(self):
        self.assertIsInstance(UserMailbox('a', 'a').auth_data, UserCredentials)

    def test_check_auth(self):
        self.assertTrue(UserMailbox('a', 'a').check(UserCredentials('a', 'a')))
        self.assertFalse(
            UserMailbox('a', 'a').check(UserCredentials('a', '2a'))
        )

    def test_close(self):
        self.assertFalse(UserMailbox('a', 'a').close())

    def test_repr_user_mailbox(self):
        self.assertIn('user@', str(UserMailbox('user@mm.com', '2')))
