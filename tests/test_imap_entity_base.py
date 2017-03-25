# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import unittest

from pymaillib.imap.entity import SlotBasedImapEntity


class BodyStructureTest(unittest.TestCase):

    def test_slot_based_imap_entity(self):

        class SomeTestClass(SlotBasedImapEntity):

            __slots__ = ('a', 'b', 'c', 'd')

        with self.assertRaises(TypeError) as exp:
            SomeTestClass()
        self.assertEqual('No Arguments provided', str(exp.exception))

        obj = SomeTestClass(1, 2, 3, 4)
        self.assertDictEqual(obj.dump(), {'a': 1, 'b': 2, 'c': 3, 'd': 4})
        obj = SomeTestClass(1, 2, 3, d=4)
        self.assertDictEqual(obj.dump(), {'a': 1, 'b': 2, 'c': 3, 'd': 4})

        with self.assertRaises(AttributeError) as _:
            SomeTestClass(1, 2, 3, 4, cddd=3)

        with self.assertRaises(TypeError) as exp:
            SomeTestClass(1, 2, 3, 4, d=3)
        self.assertEqual('Too many values provided [4] {}', str(exp.exception))
