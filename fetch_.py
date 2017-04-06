# -*- coding: utf-8 -*-
"""

"""
import imaplib
import pprint

import time

import gc

from pymaillib.imap.entity.folder import ImapFolder
from pymaillib.mailbox import UserMailbox
from pymaillib.imap.fetch_query_builder import FetchQueryBuilder
from pymaillib.settings import Config

imaplib.Debug = 0


query = FetchQueryBuilder.fast('1')
query.fetch_envelope()
#query.fetch_body_peek(3)
query.fetch_body_structure()
query.fetch_rfc822_size()

#query.fetch_header_item('Subject')
#query.fetch_header_item('Message-ID')
print(query)
#raise SystemExit


config = Config().from_config_file('./pymail.ini')

mailbox = UserMailbox('sxadmin', '1', config)
# time.sleep(1)
#list(mailbox.imap().folders())
with mailbox.imap() as client:
    with client as client2:
        print(client2.namespace())

#RFC822.HEADER RFC822.TEXT   BODY[]

    #  BODY[] BODY.PEEK[HEADER] BODY.PEEK[1.MIME] BODY.PEEK[1] RFC822
    #query.add('BODY.PEEK[HEADER.FIELDS (SUBJECT)]')
    #print(client.capabilities)
    #print(client.scalix_id())
    print(client.namespace())

    for folder in client.folders():
        print(folder)

    print(client.recent())
    raise SystemExit

    folder = ImapFolder(b'Inbox', b'/', {})
    msg = list(client.fetch(folder, query))[-1]
    pprint.pprint(dict(msg.dump()))
    pprint.pprint(msg.rfc822_size)
    pprint.pprint(msg.header_item('Message-ID'))
    #for msg in client.messages(folder, query):
    #    print(msg.uid, msg.sequence_id)
        #print(msg.envelope.subject)
        #print(msg.dump())
    #pprint(list())

#mailbox.close()
print(gc.collect())

time.sleep(15)