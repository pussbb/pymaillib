# -*- coding: utf-8 -*-
"""

"""
import unittest

import datetime

from imap.entity.email_message import ImapFetchedItem
from pymaillib.imap.entity.body_structure import BodyStructure
from pymaillib.imap.entity.envelope import Envelope, AddressList
from pymaillib.imap.parsers import ResponseTokenizer, \
    AtomTokenizer
from pymaillib.imap.utils import parse_datetime, list_to_dict, \
    build_imap_response_line


class AtomParserTest(unittest.TestCase):
    def test_parse_date(self):
        dates = [
            b'11-Nov-2015 08:37:14 -0500',
            b'11-Nov-2015 08:37:14',
            b'11-Nov-2015T19:20:30+01:00',
            b'Mon, 7 Feb 1994 21:52:25 -0800 (PST)'
        ]
        for date in dates:
            self.assertIsInstance(parse_datetime(date), datetime.datetime)

    def test_envelop_empty_subj(self):
        lines = [
            b'1 (UID 387 ENVELOPE ("Wed, 11 Nov 2015 08:37:14 -0500" "" '
            b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) ((NIL NIL '
            b'"MAIL-SYSTEM" "test.centos5486.com")) ((NIL NIL "MAIL-SYSTEM" '
            b'"test.centos5486.com")) ((NIL NIL "scalix-usage-stats"'
            b' "scalix.com")) NIL NIL NIL "<H0000000000354e1.1447249034.'
            b'test.centos5486.com@MHS>")))',

            b'2 (UID 383 ENVELOPE ("Wed, 11 Nov 2015 08:37:14 -0500" NIL'
            b' ((NIL NIL "MAIL-SYSTEM" "test.centos5486.com"))'
            b' ((NIL NIL "MAIL-SYSTEM" "test.centos5486.com"))'
            b' ((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
            b'((NIL NIL "scalix-usage-stats" "xxxxx.com")) '
            b'NIL NIL NIL "<H0000000000354e1.1447249034.test.centos5486.com'
            b'@MHS>")))',
        ]
        items = self.parse_items(lines)
        self.assertEqual(len(items), 2)
        for msg in items:
            self.assertIn(msg['ENVELOPE'].subject, (None, ''))

    def test_envelope_subj_with_other_tokens(self):
        lines = [
            b'1 (UID 387 ENVELOPE ("Wed, 11 Nov 2015 08:37:14 -0500" " dsfd'
            b' ( ss ) # ( " ((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
            b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
            b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
            b'((NIL NIL "scalix-usage-stats" "ssss.com")) NIL NIL NIL '
            b'"<H0000000000354e1.1447249034.test.centos5486.com@MHS>")))',

            b'2 (UID 383 ENVELOPE ("Wed, 11 Nov 2015 08:37:14 -0500" '
            b'"sdfs 333 \\" NIL  (NIL" ((NIL NIL "MAIL-SYSTEM" '
            b'"test.centos5486.com")) ((NIL NIL "MAIL-SYSTEM" '
            b'"test.centos5486.com")) ((NIL NIL "MAIL-SYSTEM" '
            b'"test.centos5486.com")) ((NIL NIL "scalix-usage-stats" '
            b'"scalix.com")) NIL NIL NIL "<H0000000000354e1.1447249034.test.'
            b'centos5486.com@MHS>")))'
        ]
        items = self.parse_items(lines)
        self.assertEqual(len(items), 2)
        subjects = [
            ' dsfd ( ss ) # ( ',
            'sdfs 333 \\" NIL  (NIL',
        ]

        for msg in items:
            self.assertIn(msg['ENVELOPE'].subject, subjects)

    def test_envelope_literal_subjects(self):
        lines = [
            (
            b'1 (RFC822.SIZE 4819 INTERNALDATE "26-Nov-2015 07:25:13 -0500"'
            b' FLAGS (\\Seen) UID 702 ENVELOPE ("Tue, 6 Oct 2015 12:51:12 '
            b'-0400" {70}',   b'erwerewres - works perfect since i think yest'
                              b'erday on xxx and xxxxxx..'),
            b' (("xxx xxxx" NIL "xxx" "xxxx.com")) '
            b'(("xxx xxx" NIL "xxx" "xxxx.com")) '
            b'(("xxxxx xxxxx" NIL "xxxx" "xxxxx.com")) '
            b'(("xxxx xxx" NIL "xxxx" "xxxx.com")'
            b'("xxxxx xxxx" NIL "xxxx" "xxxx.com")'
            b'("xxx" NIL "xxxx" "xxxxxx.com")) NIL NIL NIL '
            b'"<H000025c0092abea.1444150271.xxxx.xxxx.com@MHS>") '
            b'BODYSTRUCTURE (("text" "plain" ("charset" "UTF-8") NIL NIL '
            b'"quoted-printable" 615 42 NIL ("inline" NIL) NIL NIL)'
            b'("text" "html" ("charset" "us-ascii") NIL NIL "quoted-printable"'
            b' 3379 95 NIL ("inline" NIL) NIL NIL) "alternative" ("boundary"'
            b' "2_0_20a_2b33387MHTML_=_01") NIL NIL NIL))']
        items = self.parse_items(lines)
        self.assertEqual(len(items), 1)

    def test_parse_line(self):
        line = [
            b'1 (UID 387 INTERNALDATE "11-Nov-2015 08:37:14 -0500" '
            b'BODYSTRUCTURE ("text" "plain" ("charset" "US-ASCII") NIL NIL '
            b'"quoted-printable" 388 20 NIL ("inline" NIL) NIL) RFC822.SIZE'
            b' 812 FLAGS (\\Seen) ENVELOPE ("Wed, 11 Nov 2015 08:37:14 -0500" '
            b'"PHONEHOME \\" dfdf"'
            b' ((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
            b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com"))'
            b' ((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
            b'((NIL NIL "scalix-usage-stats" "sss.com")) NIL NIL NIL '
            b'"<H0000000000354e1.1447249034.test.centos5486.com@MHS>"))']

        items = self.parse_items(line)
        self.assertEqual(len(items), 1)
        msg = items[0]
        dict_keys = ['UID', 'BODYSTRUCTURE', 'RFC822.SIZE', 'ENVELOPE',
                     'FLAGS', 'SEQ']
        for key in dict_keys:
            self.assertIn(key, msg)

        self.assertIsInstance(msg['UID'], int)
        self.assertEqual(msg['UID'], 387)

        self.assertIsInstance(msg['ENVELOPE'], Envelope)
        self.assertEqual(msg['ENVELOPE'].subject, 'PHONEHOME \\" dfdf')

        self.assertIsInstance(msg['ENVELOPE'].date, datetime.datetime)
        self.assertEqual(str(msg['ENVELOPE'].date), '2015-11-11 08:37:14-05:00')

        self.assertIsInstance(msg['INTERNALDATE'], datetime.datetime)
        self.assertEqual(str(msg['INTERNALDATE']), '2015-11-11 08:37:14-05:00')

        self.assertIsNotNone(msg['ENVELOPE'].from_)
        self.assertIsInstance(msg['ENVELOPE'].from_, AddressList)

        self.assertIsNotNone(msg['FLAGS'])
        self.assertIn(b'\\Seen', msg['FLAGS'])

    def test_parse_line_with_literal(self):
        data = [(b'1 (FLAGS (\\Seen) BODY[] {812}',
                 b'Return-Path: <MAIL-SYSTEM@test.centos5486.com>\r\n'
                 b'Date: Wed, 11 Nov 2015 08:37:14 -0500\r\n'
                 b'From: MAIL-SYSTEM@test.centos5486.com\r\n'
                 b'To: scalix-usage-stats@xxxxxx.com\r\n'
                 b'Message-ID: <H0000000000354e1.1447249034.test.'
                 b'centos5486.com@MHS>\r\n'
                 b'Subject: PHONEHOME\r\n'
                 b'MIME-Version: 1.0\r\n'
                 b'X-Scalix-DRef: 0001397c8b774efa\r\n'
                 b'Content-Type: text/plain;\r\n\t'
                 b'charset="US-ASCII"\r\n'
                 b'Content-Transfer-Encoding: quoted-printable\r\n'
                 b'Content-Disposition: inline\r\n\r\n'
                 b'SCALIX-STATS-START\r\n'
                 b'SystemId=3D5630cee8ca5f3b24\r\n'
                 b'Premium=3D101\r\n'
                 b'Standard=3D1\r\n'
                 b'Server=3D12.5.1.14746\r\n'
                 b'Tomcat=3D7.0.64\r\n'
                 b'SWA=3D12.6.0.14781\r\n'
                 b'SIS=3D12.6.0.14801\r\n'
                 b'Platform=3D12.6.0.14829\r\n'
                 b'SAC=3D12.6.0.14721\r\n'
                 b'RES=3D12.6.0.14721\r\n'
                 b'Mobile=3D\r\n'
                 b'Distribution=3DRHEL-5\r\n'
                 b'Kernel=3D2.6.18-274.17.1.el5xen\r\n'
                 b'Platform=3Di686\r\n'
                 b'Cpus=3D1\r\n'
                 b'RAM=3D2432\r\n'
                 b'Data Size=3D679600\r\n'
                 b'Store Size=3D422525\r\n'
                 b'SCALIX-STATS-END\r\n'),

                b' INTERNALDATE "11-Nov-2015 08:37:14 -0500" BODYSTRUCTURE '
                b'("text" "plain" ("charset" "US-ASCII") NIL NIL '
                b'"quoted-printable" 388 20 NIL ("inline" NIL) NIL)'
                b' UID 387 RFC822.SIZE 812 ENVELOPE ("Wed, 11 Nov 2015'
                b' 08:37:14 -0500" "PHONEHOME" '
                b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
                b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
                b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
                b'((NIL NIL "scalix-usage-stats" "sss.com"))'
                b' NIL NIL NIL "<H0000000000354e1.1447249034.test.centos5486'
                b'.com@MHS>"))',

                b'2 (UID 387 INTERNALDATE "11-Nov-2015 08:37:14 -0500" '
                b'BODYSTRUCTURE ("text" "plain" ("charset" "US-ASCII") NIL NIL '
                b'"quoted-printable" 388 20 NIL ("inline" NIL) NIL)'
                b' RFC822.SIZE 812 FLAGS (\\Seen) ENVELOPE '
                b'("Wed, 11 Nov 2015 08:37:14 -0500" "PHONEHOME \\" dfdf" '
                b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
                b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
                b'((NIL NIL "MAIL-SYSTEM" "test.centos5486.com")) '
                b'((NIL NIL "scalix-usage-stats" "sss.com")) NIL NIL NIL '
                b'"<H0000000000354e1.1447249034.test.centos5486.com@MHS>"))']
        items = self.parse_items(data)

        self.assertEqual(len(items), 2)
        msg = items[0]
        dict_keys = ['UID', 'BODYSTRUCTURE', 'RFC822.SIZE', 'ENVELOPE',
                     'FLAGS', 'SEQ', 'BODY']
        for key in dict_keys:
            self.assertIn(key, msg)

        self.assertIsInstance(msg['UID'], int)
        self.assertEqual(msg['UID'], 387)

        self.assertEqual(len(msg['BODY'][0]), 812)

    def test_rfc822_in_side_bodystructure(self):
        lines = [
            b'25 (FLAGS (\\Seen \\X-Has-Attach) BODYSTRUCTURE ('
            b'(("text" "plain" ("charset" "utf-8" "format" "flowed") NIL NIL '
            b'"quoted-printable" 555 19 NIL NIL NIL) '
            b'("text" "html" ("charset" "utf-8") NIL NIL "quoted-printable"'
            b' 1797 53 NIL NIL NIL) "alternative" ("boundary"'
            b' "------------080109040200030600090402") NIL NIL)'
            b'("MESSAGE" "RFC822" NIL NIL NIL "7BIT" 19731 '
            b'("Tue, 7 Oct 2014 09:25:38  -0400" '
            b'"Re: AW: Re: Re sdsdsd ccc xcxc xcxcx" '
            b'(("xxcxc xcxmolmueller" NIL "fff" "fff.com"))'
            b' (("xcxcx xcxcxc" NIL "sdsd" "cvcvcvcv.com"))'
            b' (("cxcx xcxcxc" NIL "xx" "xx.com")) '
            b'(("cvcv ccc" NIL "ccc.ccc" "ccc.com")'
            b'("cc ccc" NIL "ccc" "ccc.com")'
            b'("xxx xxx" NIL "xxx.xxx" "xxxx.com")'
            b'("xxx xxx" NIL "xxx" "xxx.com")) '
            b'(("xxx xxx" NIL "xxx" "xxxx.com")'
            b'("xxx xxx" NIL "xxx.xxx" "xxx.com")) NIL NIL '
            b'"<4w7ndjmiuuxmec1totxia237.1412688318967@email.android.com>") '
            b'(("text" "plain" ("charset" "utf-8") NIL NIL '
            b'"quoted-printable" 5744 173 NIL NIL NIL)("text" "html" '
            b'("charset" "utf-8") NIL NIL "quoted-printable" 11866 156 NIL '
            b'NIL NIL) "alternative" ("boundary" "--_com.android.email_'
            b'847787723214625") NIL NIL) 379 NIL ("attachment" ("filename" '
            b'"ForwardedMessage.eml")) NIL) "mixed" ("boundary" '
            b'"------------000605010102080309050007") NIL NIL) '
            b'INTERNALDATE "07-Oct-2014 11:42:29 -0400" RFC822.SIZE'
            b' 24190 UID 10563 ENVELOPE ("Tue, 7 Oct 2014 18:42:10 +0300"'
            b' "Re: AW: Re: Re sdsdsd ccc xcxc xcxcx"'
            b' (("xxx xxx" NIL "xxx" "xxx.com")) '
            b'(("xxx xxx" NIL "xxx" "xxx.com")) '
            b'(("xxx xxx" NIL "xxx" "xxxx.com"))'
            b' (("xx xxx" NIL "xxx" "xxx.com")'
            b'("xxx xxx" NIL "xxx" "xxxx.com")'
            b'("xxx xxx" NIL "xxx.xxx" "xxxx.com")'
            b'("xxxx xxxx" NIL "xxx.xxxx" "xxxx.com")'
            b'("xxxx xxx" NIL "xxx" "xxxxx.com")'
            b'("xxxx xxxxx" NIL "xxx" "xxxxx.com")) NIL NIL '
            b'"<H00000a900428af8.1412688357.mail.xxxxx.com@MHS>" '
            b'"<543409D2.8090607@xxxx.com>"))']

        items = self.parse_items(lines)

        self.assertEqual(len(items), 1)

    def test_atom_name_in_subject(self):
        lines = [
            b'2805 (RFC822.SIZE 11892 FLAGS (\\X-Has-Attach) ENVELOPE '
            b'("Mon, 7 Dec 2015 08:41:29 -0500" '
            b'"[xxxx - xxx xxxx #60164] xxxx xxx xxxx xxxx BODYSTRUCTURE '
            b'BODY[0] RFC822 \\"  RFC822.SIZE " '
            b'(("xxx" NIL "xxx" "xxx.com")) (("xxx" NIL "xxx" "xxx.com")) '
            b'(("xxx" NIL "xxx" "xxx.com")) (("xx xxx" NIL "xx" "xx.com"))'
            b' NIL NIL NIL "<H000009e00de9a79.1449495689.mail.scalix.com@MHS>")'
            b' INTERNALDATE "07-Dec-2015 08:38:58 -0500" BODYSTRUCTURE '
            b'("MESSAGE" "RFC822" NIL NIL NIL "7BIT" 10725 ("Mon, 7 Dec 2015 '
            b'08:41:35 -0500" "[xxxx - xxx xxxx #60164] xxxx xxx xxxx xxxx '
            b'BODYSTRUCTURE BODY[0] RFC822 \\"  RFC822.SIZE " '
            b'(("xxx xxx" NIL "xxxdddt" "ddd.com")) '
            b'(("xxxx xx" NIL "xxxx" "xxxxx.com")) '
            b'(("xxxx xx" NIL "xxxx" "xxxx.com"))'
            b' ((NIL NIL "undisclosed-recipients:;" "")) NIL NIL NIL'
            b' "<redmine.journal-804.20151207134134.ec073bb44061c0dd@xx.com>") '
            b'(("text" "plain" ("charset" "US-ASCII") NIL NIL "7bit" 4020 69 '
            b'NIL NIL NIL)("text" "html" ("charset" "US-ASCII") NIL NIL "7bit"'
            b' 5102 100 NIL NIL NIL) "alternative" ("charset" "UTF-8" '
            b'"boundary" "--==_mimepart_56658c8f28ea_610a27c24f883962") NIL'
            b' NIL) 211 NIL NIL NIL) UID 165359)',

        ]
        items = self.parse_items(lines)
        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0]['ENVELOPE'].subject,
            '[xxxx - xxx xxxx #60164] xxxx xxx xxxx xxxx BODYSTRUCTURE BODY[0] '
            'RFC822 \\"  RFC822.SIZE '
        )

    def test_non_extensible_body_item(self):
        lines = [
            b'1 (RFC822.SIZE 4819 FLAGS (\\Seen) INTERNALDATE '
            b'"26-Nov-2015 07:25:13 -0500" UID 702 BODYSTRUCTURE '
            b'(("text" "plain" ("charset" "UTF-8") NIL NIL "quoted-printable" '
            b'615 42 NIL ("inline" NIL) NIL NIL)("text" "html" '
            b'("charset" "us-ascii") NIL NIL "quoted-printable" 3379 95 NIL '
            b'("inline" NIL) NIL NIL) "alternative" ("boundary" '
            b'"2_0_20a_2b33387MHTML_=_01") NIL NIL NIL) BODY '
            b'(("text" "plain" ("charset" "UTF-8") NIL NIL'
            b' "quoted-printable" 615 42)("text" "html" ("charset" "us-ascii")'
            b' NIL NIL "quoted-printable" 3379 95) "alternative"))'
        ]

        items = self.parse_items(lines)
        self.assertEqual(len(items), 1)
        self.assertIsInstance(items[0]['BODYSTRUCTURE'], BodyStructure)

    def parse_items(self, items):
        res = []
        for line, literals in build_imap_response_line(items):
            res.append(ImapFetchedItem(AtomTokenizer(line, literals).items()))
        return res

    def test_empty_body_repsponse(self):
        lines = [
            (b'1 (UID 702 FLAGS (\\Seen) RFC822.SIZE 4819 INTERNALDATE'
             b' "26-Nov-2015 07:25:13 -0501" BODY[88] {0}', b''), b')',
            b'2 (FLAGS (\\Seen) UID 1 INTERNALDATE '
            b'"04-Dec-2015 02:50:48 -0502" BODY[88] NIL RFC822.SIZE 1020)',
            b'3 (FLAGS (\\Seen) UID 1 INTERNALDATE'
            b' "04-Dec-2015 02:50:48 -0503" BODY[88] "" RFC822.SIZE 1020)'
        ]

        items = self.parse_items(lines)
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertIn(item['BODY']['88'], [b'', None])

    def test_enveloper_more_literal(self):
        lines = [
            (
            b'1 (INTERNALDATE "29-Dec-2015 04:08:16 -0500" FLAGS (\\Seen) '
            b'RFC822.SIZE 10322 UID 1 ENVELOPE '
            b'("Mon, 28 Dec 2015 10:40:45 +0000" "xxxx/xxxxx Meeting" (({14}',
            b'Xxxxxx Xxxxxxx'), (b' NIL "xx" "xxx.com")) (({14}',
                                 b'Xxxxxx Xxxxxxx'),

            (b' NIL "ob" "xxxxx.com")) (({14}', b'Xxxxxx Xxxxxxx'),
            b' NIL "ob" "xxxxx.com")) ((NIL NIL "xxxxx" "MISSING_DOMAIN"))'
            b' NIL NIL NIL "<DM2PR04MB73356088E83B2FDF569C0B3B9FB0@DM2PR04MB733'
            b'.namprd04.prod.xxxxx.com>"))',

            ( b'2 (INTERNALDATE "29-Dec-2015 04:08:16 -0500" FLAGS (\\Seen) '
              b'RFC822.SIZE 10322 UID 1 ENVELOPE ("Mon, 28 Dec 2015 10:40:45 '
              b'+0000" "xxxxx/xxxx xxxxx" (({14}', b'Xxxxx Xxxxxxxx'),
              (b' NIL "ob" "xxx.com")) (({14}', b'Xxxxxx Xxxxxxx'),

            (b' NIL "ob" "xxx.com")) (({14}',  b'Xxxxxx Xxxxxxx'),
            (b' NIL "ob" "xxxx.com")) ((NIL NIL "xxxx" "MISSING_DOMAIN")) NIL '
             b'NIL NIL "<DM2PR04MB73356088E83B2FDF569C0B3B9FB0@DM2PR04MB733.'
             b'namprd04.prod.xxxx.com>") BODY[] {14}', b'Xxxxxx Xxxxxxx'),
            b')',
        ]
        items = self.parse_items(lines)
        self.assertEqual(len(items), 2)
        self.assertIsNotNone(items[1]['BODY'])

    def test_handle_custom_atom(self):
        lines = [
            (b'1 (UID 702 FLAGS (\\Seen) RFC822.SIZE 4819 INTERNALDATE'
             b' "26-Nov-2015 07:25:13 -0500" X-DAV-BODY {0}', b''), b')',
            b'2 (FLAGS (\\Seen) UID 1 INTERNALDATE '
            b'"04-Dec-2015 02:50:48 -0502" X-DAV-BODY[88] NIL RFC822.SIZE 1020)',
            b'3 (FLAGS (\\Seen) UID 1 INTERNALDATE '
            b'"04-Dec-2015 02:50:48 -0503" X-DAV-BODY[88] "" RFC822.SIZE 1020)'
        ]
        items = self.parse_items(lines)

        self.assertEqual(len(items), 3)

        for item in items:
            self.assertIn('X-DAV-BODY', item)
            self.assertIsNotNone(item['X-DAV-BODY'])

    def test_atom_parser_literal_complex(self):
        lines = [
            (b'1 (FLAGS (\\Seen) RFC822.SIZE 10322 UID 1 INTERNALDATE'
             b' "29-Dec-2015 04:08:16 -0500" ENVELOPE '
             b'("Mon, 28 Dec 2015 10:40:45 +0000" "xxx/xxx xxxx" (({14}',
             b'Xxxxxx Xxxxxxx'),
            (b' NIL "ob" "xxxxx.com")) (({14}', b'Xxxxxx Xxxxxxx'),
            (b' NIL "ob" "xxx.com")) (({14}',  b'Xxxxxx Xxxxxxx'),
            (b' NIL "ob" "xxx.com")) ((NIL NIL "xxxx" "MISSING_DOMAIN")) NIL'
             b' NIL NIL "<DM2PR04MB73356088E83B2FDF569C0B3B9FB0@DM2PR04MB733.'
             b'namprd04.prod.xxx.com>") BODY[HEADER.FIELDS (SUBJECT)] {31}',
            b'Subject: XXX/XXXXXX Meeting\r\n\r\n'), b')'
        ]

        items = self.parse_items(lines)
        self.assertEqual(len(items), 1)
        msg = items[0]
        self.assertIsNotNone(msg['ENVELOPE'])
        self.assertIsInstance(msg['ENVELOPE'], Envelope)
        self.assertIsNotNone(msg['BODY'])
        self.assertIn('HEADER.FIELDS (SUBJECT)', msg['BODY'])
        self.assertIsNotNone(msg['BODY']['HEADER.FIELDS (SUBJECT)'])

    def test_user_name_integer_in_bodystruct(self):
        lines = [
            b'1 (BODYSTRUCTURE (("text" "plain" ("charset" "UTF-8") NIL NIL '
            b'"quoted-printable" 1179 46 NIL NIL NIL)("text" "html" '
            b'("charset" "UTF-8") NIL NIL "quoted-printable" 3629 65 NIL NIL'
            b' NIL) "alternative" ("boundary" "----=_NextPart_54368DB1_08F84D18'
            b'_4DFC5ECA") NIL NIL) FLAGS (\\Seen) RFC822.SIZE 8197 UID 10917 '
            b'ENVELOPE ("Thu, 9 Oct 2014 21:29:21 +0800" "Re:xxx xxx xxx '
            b'xxx xxx" (("2383752080" NIL "2383752080" "xxx.com")) '
            b'(("2383752080" NIL "2383752080" "xxx.com")) '
            b'(("2383752080" NIL "2383752080" "qq.com")) '
            b'(("xxx" NIL "xxx" "xxxxx.com")) NIL NIL "<5645effe30c90dc5dee7b'
            b'5fe065919cf@billing.xxxxxx.com>" '
            b'"<tencent_4A5FB0321B6AF0D66F2FA297@xxxx.com>") '
            b'INTERNALDATE "09-Oct-2014 09:29:58 -0400")'
        ]
        items = self.parse_items(lines)
        self.assertEqual(len(items), 1)

    def test_magic_number_41(self):
        lines = [
            b'1 (BODYSTRUCTURE (("text" "plain" ("charset" "UTF-8") NIL NIL '
            b'"quoted-printable" 1179 41 NIL NIL NIL)("text" "html" '
            b'("charset" "UTF-8") NIL NIL "quoted-printable" 3629 65 NIL NIL '
            b'NIL) "alternative" ("boundary" "----=_NextPart_54368DB1_08F84D18'
            b'_4DFC5ECA") NIL NIL) FLAGS (\\Seen) RFC822.SIZE 8197 UID 10917 '
            b'ENVELOPE ("Thu, 9 Oct 2014 21:29:21 +0800" "xxxx:xxx xxx xxx xxx xxx" '
            b'(("2383752080" NIL "2383752080" "xxx.com")) (("2383752080" NIL '
            b'"2383752080" "xxx.com")) (("2383752080" NIL "2383752080" '
            b'"xxx.com")) (("xxx" NIL "xxx" "xxxx.com")) NIL NIL '
            b'"<5645effe30c90dc5dee7b5fe065919cf@billing.xxxxx.com>" '
            b'"<tencent_4A5FB0321B6AF0D66F2FA297@ccc.com>") INTERNALDATE '
            b'"09-Oct-2014 09:29:58 -0400")'
        ]
        items = self.parse_items(lines)
        self.assertEqual(len(items), 1)
        self.assertGreater(len(items[0]), 2)

    def test_x_scalix_id_(self):
        lines = [
            b'("name" "imap41d" "version" "12.6.0.14933" "os" "CentOS release'
            b' 6.8 (Final)" "os-version" "2.6.32-642.11.1.el6.x86_64"'
            b' "date" "22-Mar-2017 07:35:48 -0400" "display-name" '
            b'"ss sss" "mail-address" "sss@sss.com" "auth-id" "sss@ssss.ssss"'
            b' "global-unique-id" "1LRhv2l8mkip446eFB1PfA==")'
        ]
        line = list(ResponseTokenizer(lines[0], []))
        self.assertIsNotNone(line)
        self.assertEquals(len(line), 1)
        self.assertNotEquals(list_to_dict(line[0]), [])

    def test_dolar_sign(self):

        lines = [
            b'1983 (ENVELOPE ("Mon, 20 Mar 2017 14:30:02 +0200"'
            b' "Fwd: xxx xxx and xxxxx" (("s as" NIL "xxxx" "as.com"))'
            b' (("as as" NIL "xxx" "as.com")) (("as as" NIL "sa" "as.com")) '
            b'(("as sa" NIL "as" "sa.com")) NIL NIL '
            b'"<H000025c01144f6d.1489963577.as.as.com@MHS>" '
            b'"<65ae1793-08e8-0173-1d88-d7abfffd7dd2@ccc.com>") BODYSTRUCTURE '
            b'(("text" "plain" ("charset" "UTF-8" "format" "flowed") NIL NIL '
            b'"quoted-printable" 2363 74 NIL NIL NIL)("text" "html" '
            b'("charset" "UTF-8") NIL NIL "quoted-printable" 14322 363 NIL NIL'
            b' NIL) "alternative" ("boundary" "------------F1958828B762A9E6AB3C'
            b'1D56") NIL NIL) FLAGS (\\Seen $Forwarded \\X-Forwarded) '
            b'UID 284465 RFC822.SIZE 18137 INTERNALDATE "20-Mar-2017 08:27:46 '
            b'-0400")'
        ]
        items = self.parse_items(lines)
        self.assertEquals(items[0]['FLAGS'],
                          [b'\\Seen', b'$Forwarded', b'\\X-Forwarded'])

    def test_response_tokenizer(self):
        lines = [
            (
                b'888 (UID 333 X-ENVELOPE ((nil nil nil) nil))',
                [888, [b'UID', 333, b'X-ENVELOPE', [[None, None, None], None]]]
            ),
            (
                b'(\\Unselect) "/" Trash',
                [[b'\\Unselect'], b'/', b'Trash']
            ),
            (
                b'() "/" Trash',
                [[], b'/', b'Trash']
            )
        ]

        for line in lines:
            self.assertEqual(list(ResponseTokenizer(line[0], [])), line[1])
