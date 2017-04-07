# -*- coding: utf-8 -*-
"""
    Imap4 constants
    ~~~~~~~~~~~~~~~~
    Imap4 constants

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib
import re

IMAP_DEFAULTS = {
    'host': '',
    'port': imaplib.IMAP4_PORT,
    'secure': False,
    'keyfile': None,
    'certfile': None
}

IMAP4_COMMANDS = {'CAPABILITY', 'LOGOUT', 'LOGIN', 'DELETE', 'RENAME', 'CREATE',
                  'EXAMINE', 'SELECT', 'NOOP', 'SUBSCRIBE', 'UNSUBSCRIBE',
                  'LIST', 'LSUB', 'APPEND', 'CHECK', 'CLOSE', 'EXPUNGE',
                  'SEARCH', 'FETCH', 'PARTIAL', 'STORE', 'COPY', 'UID'}

IMAP4REV1_CAPABILITY_KEYS = {'IMAP4rev1', 'IMAP4REV1'}

FOLDER_UNTAGGED_KEYS = ('FLAGS', 'RECENT', 'UNSEEN', 'UIDVALIDITY', 'UIDNEXT',
                        'PERMANENTFLAGS')

IMAP4_OK_RESULT = 'OK'
IMAP4_NO_RESULT = 'NO'
IMAP4_BAD_REQUEST = 'BAD'

IMAP4_FOLDER_SPECIAL_CHARS = re.compile(b'([\s,/"]+)')

#  NOT USED FOR NOW
IMAP_SPECIAL_FLAGS = [
    'ANSWERED',
    'DELETED',
    'DRAFT',
    'FLAGGED',
    'RECENT',
    'SEEN',
    'UNSEEN',
]

FLAG_DELETED = r'\Deleted'
FLAG_SEEN = r'\Seen'
FLAG_ANSWERED = r'\Answered'
FLAG_FLAGGED = r'\Flagged'
FLAG_DRAFT = r'\Draft'
FLAG_RECENT = r'\Recent'
