# -*- coding: utf-8 -*-
"""

"""
import imaplib
import pprint
import os

from pymaillib.imap.entity.folder import ImapFolder
from pymaillib.mailbox import UserMailbox
from pymaillib.imap.fetch_query_builder import FetchQueryBuilder
from pymaillib.settings import Config

imaplib.Debug = 0

query = FetchQueryBuilder.fast(sequence=1)
query.fetch_envelope()
query.fetch_body_peek()
print(query)
#raise SystemExit


config = Config().from_config_file('./pymail.ini')

mailbox = UserMailbox('sxadmin', '1', config)
# time.sleep(1)

with mailbox.imap() as client:
#RFC822.HEADER RFC822.TEXT   BODY[]

    #  BODY[] BODY.PEEK[HEADER] BODY.PEEK[1.MIME] BODY.PEEK[1] RFC822
    #query.add('BODY.PEEK[HEADER.FIELDS (SUBJECT)]')

    for folder in client.folders():
        print(folder)

    folder = ImapFolder(b'Inbox', b'/', {})
    pprint.pprint(len(list(client.messages(folder, query))))
    #for msg in client.messages(folder, query):
    #    print(msg.uid, msg.sequence_id)
        #print(msg.envelope.subject)
        #print(msg.dump())
    #pprint(list())

