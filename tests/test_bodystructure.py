# -*- coding: utf-8 -*-
"""

"""
import unittest

from pymaillib.imap.entity.body_structure import BodyStructure, SimpleBodyPart, \
    MultiPartBodyPart, MessageRFC822BodPart
from pymaillib.imap.entity.envelope import Envelope


class BodyStructureTest(unittest.TestCase):

    def test_simple(self):
        data = [b'text', b'plain', [b'charset', b'US-ASCII'], None, None,
                b'quoted-printable', 388, 20, None, [b'inline', None], None]

        obj = BodyStructure.build(data)
        self.assertFalse(obj.is_multipart())
        self.assertIsInstance(obj.part, SimpleBodyPart)
        self.assertEqual(obj.part.content_part, b'text/plain')
        self.assertEqual(obj.part.encoding, b'quoted-printable')
        self.assertEqual(obj.part.charset, b'US-ASCII')

    def test_simple_non_text(self):
        data = [b'application', b'scalix-properties', None, None,
                        None, b'7bit', 1671, None, None, None, None]

        obj = BodyStructure.build(data)
        self.assertFalse(obj.is_multipart())
        self.assertIsInstance(obj.part, SimpleBodyPart)
        self.assertEqual(obj.part.content_part,
                         b'application/scalix-properties')
        self.assertEqual(obj.part.encoding, b'7bit')

    def test_alternative(self):
        data = [[b'text', b'plain', [b'charset', b'iso-8859-1'], None, None,
                 b'quoted-printable', 5845, 261, None, None, None],
                [b'text', b'html', [b'charset', b'iso-8859-1'], None, None,
                 b'quoted-printable', 35380, 1158, None, None, None],
                b'alternative',
                [b'boundary', b'----=_Part_310_216476006.1412669886901'],
                None, None]

        obj = BodyStructure.build(data)
        self.assertTrue(obj.is_multipart())
        self.assertIsInstance(obj.part, MultiPartBodyPart)
        self.assertEqual(len(obj.part.parts), 2)
        self.assertIsNotNone(obj.part.boundary)

    def test_mixed_one_attachment(self):
        data = [[[b'text', b'plain', [b'charset', b'us-ascii'], None, None,
                  b'7bit', 13, 0, None, None, None],
                 [b'text', b'html', [b'charset', b'us-ascii'], None, None,
                  b'7bit', 177, 0, None, None, None], b'alternative',
                 [b'boundary', b'----=_Part_1_30234291.1448461057725'],
                 None, None],
                [b'application', b'pdf',
                 [b'name',
                  b'=?UTF-8?Q?enjoy_-_=D0=B4?= =?UTF-8?Q?=D0=B0=D1=82=D0'
                  b'=B0_=D0=BD=D0=B0=D0=B8=D0=BC=D0=B5=D0=BD?= =?UTF-8?Q'
                  b'?=D0=BE=D0=B2=D0=B0=D0=BD=D0=B8=D0=B5_-_Sheet1.pdf?='],
                 None, None, b'base64', 38366, None,
                 [b'attachment',
                  [b'filename',
                   b'=?UTF-8?Q?enjoy_-_=D0=B4=D0=B0=D1=82=D0=B0_=D0=BD=D0'
                   b'=B0=D0=B8=D0=BC=D0=B5=D0=BD=D0=BE=D0=B2=D0=B0=D0=BD='
                   b'D0=B8=D0=B5_-_Sheet1.pdf?=']], None],
                b'mixed',
                [b'boundary', b'----=_Part_0_28145835.1448461057725'], None,
                None]

        obj = BodyStructure.build(data)
        self.assertTrue(obj.is_multipart())
        self.assertIsInstance(obj.part, MultiPartBodyPart)
        self.assertEqual(len(obj.part.parts), 2)
        self.assertIsInstance(obj.part.parts[0], MultiPartBodyPart)
        self.assertIsNotNone(obj.part.parts[1].filename)
        self.assertIsNotNone(obj.part.boundary)

    def test_mixed_two_attachments(self):
        data = [[[b'text', b'plain', [b'charset', b'us-ascii'], None, None,
                  b'7bit', 6, 0, None, None, None], [b'text', b'html',
                                                     [b'charset', b'us-ascii'],
                                                     None, None, b'7bit', 170,
                                                     0,
                                                     None, None, None],
                 b'alternative', [b'boundary',
                                  b'----=_Part_1_8099118.1448518502536'], None,
                 None],
                [b'application', b'pdf',
                    [b'name',
                     b'=?UTF-8?Q?enjoy_-_=D0=B4?= =?UTF-8?Q?=D0=B0=D1=82=D0'
                     b'=B0_=D0=BD=D0=B0=D0=B8=D0=BC=D0=B5=D0=BD?= =?UTF-8?Q'
                     b'?=D0=BE=D0=B2=D0=B0=D0=BD=D0=B8=D0=B5_-_Sheet1.pdf?='],
                    None, None, b'base64', 38366, None,
                    [b'attachment',
                     [b'filename',
                      b'=?UTF-8?Q?enjoy_-_=D0=B4=D0=B0=D1=82=D0=B0_=D0=BD=D0'
                      b'=B0=D0=B8=D0=BC=D0=B5=D0=BD=D0=BE=D0=B2=D0=B0=D0=BD='
                      b'D0=B8=D0=B5_-_Sheet1.pdf?=']], None],
                [b'application',
                 b'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                 [b'name',
                  b'=?UTF-8?B?ZW5qb3kgLSDQtNCw0YLQsCDQvdCw?= =?UTF-8?B?0'
                  b'LjQvNC10L3QvtCy0LDQvdC40LUueGxzeA==?='],
                 None, None, b'base64', 6788, None,
                 [b'attachment',
                  [b'filename',
                   b'=?UTF-8?Q?enjoy_-_=D0=B4=D0=B0=D1=82=D0=B0_=D0=BD=D0'
                   b'=B0=D0=B8=D0=BC=D0=B5=D0=BD=D0=BE=D0=B2=D0=B0=D0=BD='
                   b'D0=B8=D0=B5.xlsx?=']], None], b'mixed',
                [b'boundary', b'----=_Part_0_4236961.1448518502536'], None,
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
        data = [[[b'text', b'plain',
                  [b'charset', b'utf-8', b'format', b'flowed'], None,
                  None, b'quoted-printable', 555, 19, None, None, None, None],
                 [b'text', b'html', [b'charset', b'utf-8'], None, None,
                  b'quoted-printable', 1797, 53, None, None, None, None],
                 b'alternative',
                 [b'boundary', b'------------080109040200030600090402'],
                 None, None, None],
                [b'message', b'rfc822', [b'name', b'ForwardedMessage.eml'],
                 None, None, b'7bit', 19739,
                 [b'Tue, 7 Oct 2014 09:25:38 -0400',
                    b'Re: AW: Re: xxx xxx xxx xxx xxxx',
                  [[b'xx xx', None, b'xx', b'xx.com']],
                  [[b'xxx xxx', None, b'xxx', b'xxx.com']],
                  [[b'xx xxx', None, b'xxx', b'xxx.com']],
                  [[b'xxx xxx', None, b'xxx.xxx',b'xx.com'],
                   [b'xx xx', None, b'ffff', b'xx.com'],
                   [b'xx xx', None, b'xx.xxx', b'xx.com'],
                   [b'xxx xxx', None, b'xxx', b'xxx.com']],
                  [[b'xxx xxx', None, b'xxx', b'xxx.com'],
                   [b'xxx xx', None, b'xxx.xxx', b'xxx.com']],
                  None, None, b'<4w7ndjmiuuxmec1totxia237.1412688318967@e'
                              b'mail.android.com>'],
                 [[b'text', b'plain', [b'charset', b'utf-8'], None, None,
                   b'quoted-printable', 5744, 173, None, None, None, None],
                  [b'text', b'html', [b'charset', b'utf-8'], None, None,
                   b'quoted-printable', 11866, 156, None, None, None,  None],
                  b'alternative', [b'boundary', b'--_com.android.email_84'
                                                b'7787723214625'],
                  None, None, None], 382, None, [b'attachment',
                                                 [b'filename',
                                                  b'ForwardedMessage.eml']],
                 None, None
                 ], b'mixed',
                [b'boundary', b'------------000605010102080309050007'],
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
