# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import os
import unittest

import pymaillib.settings as mailsettings
from importlib import reload


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.test_conf = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'test_settings.ini',
        )
        self.mailsettings = mailsettings

    def reload_settings(self):
        os.environ['PYMAILLIB_CONFIG'] = self.test_conf
        reload(mailsettings)

