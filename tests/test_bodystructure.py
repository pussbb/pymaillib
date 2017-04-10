# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import unittest

from pymaillib.imap.entity.body_structure import BodyStructure, SimpleBodyPart,\
    MultiPartBodyPart, MessageRFC822BodPart
from pymaillib.imap.entity.envelope import Envelope


class BodyStructureTest(unittest.TestCase):

    def test_simple(self):
        data = ['text', 'plain', ['charset', 'US-ASCII'], None, None,
                'quoted-printable', 388, 20, None, ['inline', None], None]

        obj = BodyStructure.build(data)
        self.assertFalse(obj.is_multipart())
        self.assertIsInstance(obj.part, SimpleBodyPart)
        self.assertEqual(obj.part.content_part, 'text/plain')
        self.assertEqual(obj.part.encoding, 'quoted-printable')
        self.assertEqual(obj.part.charset, 'US-ASCII')

    def test_simple_non_text(self):
        data = ['application', 'scalix-properties', None, None,
                        None, '7bit', 1671, None, None, None, None]

        obj = BodyStructure.build(data)
        self.assertFalse(obj.is_multipart())
        self.assertIsInstance(obj.part, SimpleBodyPart)
        self.assertEqual(obj.part.content_part,
                         'application/scalix-properties')
        self.assertEqual(obj.part.encoding, '7bit')

    def test_alternative(self):
        data = [['text', 'plain', ['charset', 'iso-8859-1'], None, None,
                 'quoted-printable', 5845, 261, None, None, None],
                ['text', 'html', ['charset', 'iso-8859-1'], None, None,
                 'quoted-printable', 35380, 1158, None, None, None],
                'alternative',
                ['boundary', '----=_Part_310_216476006.1412669886901'],
                None, None]

        obj = BodyStructure.build(data)
        self.assertTrue(obj.is_multipart())
        self.assertIsInstance(obj.part, MultiPartBodyPart)
        self.assertEqual(len(obj.part.parts), 2)
        self.assertIsNotNone(obj.part.boundary)

    def test_mixed_one_attachment(self):
        data = [[['text', 'plain', ['charset', 'us-ascii'], None, None,
                  '7bit', 13, 0, None, None, None],
                 ['text', 'html', ['charset', 'us-ascii'], None, None,
                  '7bit', 177, 0, None, None, None], 'alternative',
                 ['boundary', '----=_Part_1_30234291.1448461057725'],
                 None, None],
                ['application', 'pdf',
                 ['name',
                  '=?UTF-8?Q?enjoy_-_=D0=B4?= =?UTF-8?Q?=D0=B0=D1=82=D0'
                  '=B0_=D0=BD=D0=B0=D0=B8=D0=BC=D0=B5=D0=BD?= =?UTF-8?Q'
                  '?=D0=BE=D0=B2=D0=B0=D0=BD=D0=B8=D0=B5_-_Sheet1.pdf?='],
                 None, None, 'base64', 38366, None,
                 ['attachment',
                  ['filename',
                   '=?UTF-8?Q?enjoy_-_=D0=B4=D0=B0=D1=82=D0=B0_=D0=BD=D0'
                   '=B0=D0=B8=D0=BC=D0=B5=D0=BD=D0=BE=D0=B2=D0=B0=D0=BD='
                   'D0=B8=D0=B5_-_Sheet1.pdf?=']], None],
                'mixed',
                ['boundary', '----=_Part_0_28145835.1448461057725'], None,
                None]

        obj = BodyStructure.build(data)
        self.assertTrue(obj.is_multipart())
        self.assertIsInstance(obj.part, MultiPartBodyPart)
        self.assertEqual(len(obj.part.parts), 2)
        self.assertIsInstance(obj.part.parts[0], MultiPartBodyPart)
        self.assertIsNotNone(obj.part.parts[1].filename)
        self.assertIsNotNone(obj.part.boundary)

    def test_mixed_two_attachments(self):
        data = [[['text', 'plain', ['charset', 'us-ascii'], None, None,
                  '7bit', 6, 0, None, None, None], ['text', 'html',
                                                     ['charset', 'us-ascii'],
                                                     None, None, '7bit', 170,
                                                     0,
                                                     None, None, None],
                 'alternative', ['boundary',
                                  '----=_Part_1_8099118.1448518502536'], None,
                 None],
                ['application', 'pdf',
                    ['name',
                     '=?UTF-8?Q?enjoy_-_=D0=B4?= =?UTF-8?Q?=D0=B0=D1=82=D0'
                     '=B0_=D0=BD=D0=B0=D0=B8=D0=BC=D0=B5=D0=BD?= =?UTF-8?Q'
                     '?=D0=BE=D0=B2=D0=B0=D0=BD=D0=B8=D0=B5_-_Sheet1.pdf?='],
                    None, None, 'base64', 38366, None,
                    ['attachment',
                     ['filename',
                      '=?UTF-8?Q?enjoy_-_=D0=B4=D0=B0=D1=82=D0=B0_=D0=BD=D0'
                      '=B0=D0=B8=D0=BC=D0=B5=D0=BD=D0=BE=D0=B2=D0=B0=D0=BD='
                      'D0=B8=D0=B5_-_Sheet1.pdf?=']], None],
                ['application',
                 'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                 ['name',
                  '=?UTF-8?B?ZW5qb3kgLSDQtNCw0YLQsCDQvdCw?= =?UTF-8?B?0'
                  'LjQvNC10L3QvtCy0LDQvdC40LUueGxzeA==?='],
                 None, None, 'base64', 6788, None,
                 ['attachment',
                  ['filename',
                   '=?UTF-8?Q?enjoy_-_=D0=B4=D0=B0=D1=82=D0=B0_=D0=BD=D0'
                   '=B0=D0=B8=D0=BC=D0=B5=D0=BD=D0=BE=D0=B2=D0=B0=D0=BD='
                   'D0=B8=D0=B5.xlsx?=']], None], 'mixed',
                ['boundary', '----=_Part_0_4236961.1448518502536'], None,
                None]
        obj = BodyStructure.build(data)
        self.assertTrue(obj.is_multipart())
        self.assertIsInstance(obj.part, MultiPartBodyPart)

        self.assertEqual(len(obj.part.parts), 3)
        self.assertIsInstance(obj.part.parts[0], MultiPartBodyPart)
        self.assertIsNotNone(obj.part.parts[1].filename)
        self.assertIsNotNone(obj.part.parts[2].filename)
        self.assertIsNotNone(obj.part.boundary)

    def test_mixed_message_rfc822(self):
        data = [[['text', 'plain',
                  ['charset', 'utf-8', 'format', 'flowed'], None,
                  None, 'quoted-printable', 555, 19, None, None, None, None],
                 ['text', 'html', ['charset', 'utf-8'], None, None,
                  'quoted-printable', 1797, 53, None, None, None, None],
                 'alternative',
                 ['boundary', '------------080109040200030600090402'],
                 None, None, None],
                ['message', 'rfc822', ['name', 'ForwardedMessage.eml'],
                 None, None, '7bit', 19739,
                 ['Tue, 7 Oct 2014 09:25:38 -0400',
                    'Re: AW: Re: xxx xxx xxx xxx xxxx',
                  [['xx xx', None, 'xx', 'xx.com']],
                  [['xxx xxx', None, 'xxx', 'xxx.com']],
                  [['xx xxx', None, 'xxx', 'xxx.com']],
                  [['xxx xxx', None, 'xxx.xxx','xx.com'],
                   ['xx xx', None, 'ffff', 'xx.com'],
                   ['xx xx', None, 'xx.xxx', 'xx.com'],
                   ['xxx xxx', None, 'xxx', 'xxx.com']],
                  [['xxx xxx', None, 'xxx', 'xxx.com'],
                   ['xxx xx', None, 'xxx.xxx', 'xxx.com']],
                  None, None, '<4w7ndjmiuuxmec1totxia237.1412688318967@e'
                              'mail.android.com>'],
                 [['text', 'plain', ['charset', 'utf-8'], None, None,
                   'quoted-printable', 5744, 173, None, None, None, None],
                  ['text', 'html', ['charset', 'utf-8'], None, None,
                   'quoted-printable', 11866, 156, None, None, None,  None],
                  'alternative', ['boundary', '--_com.android.email_84'
                                                '7787723214625'],
                  None, None, None], 382, None, ['attachment',
                                                 ['filename',
                                                  'ForwardedMessage.eml']],
                 None, None
                 ], 'mixed',
                ['boundary', '------------000605010102080309050007'],
                None, None, None]

        obj = BodyStructure.build(data)
        self.assertTrue(obj.is_multipart())
        self.assertIsInstance(obj.part, MultiPartBodyPart)
        self.assertEqual(len(obj.part.parts), 2)
        self.assertIsInstance(obj.part.parts[0], MultiPartBodyPart)
        self.assertIsInstance(obj.part.parts[1], MessageRFC822BodPart)
        self.assertIsNotNone(obj.part.parts[1].filename)
        self.assertIsNotNone(obj.part.parts[1].envelope)
        self.assertIsNotNone(obj.part.parts[1].bodystructure)
        self.assertIsInstance(obj.part.parts[1].envelope, Envelope)
        self.assertIsInstance(obj.part.parts[1].bodystructure, BodyStructure)
        self.assertIsNotNone(obj.part.boundary)

        self.assertIsNone(obj.find_by_mime_id('8'))
        self.assertIsNotNone(obj.find_by_mime_id('1.1'))
