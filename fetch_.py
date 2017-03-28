# -*- coding: utf-8 -*-
"""

"""
import imaplib
import pprint

from pymaillib.imap.entity.folder import ImapFolder
from pymaillib.mailbox import UserMailbox
from pymaillib.imap.fetch_query_builder import FetchQueryBuilder
from pymaillib.settings import Config

imaplib.Debug = 0


query = FetchQueryBuilder.fast(sequence=1)
query.fetch_envelope()
query.fetch_body_peek(3)
query.fetch_body_structure()
query.fetch_rfc822()
#query.fetch_header_item('Subject')
#query.fetch_header_item('Message-ID')
print(query)
#raise SystemExit


config = Config().from_config_file('./pymail.ini')

mailbox = UserMailbox('sxadmin', '1', config)
# time.sleep(1)

with mailbox.imap() as client:
#RFC822.HEADER RFC822.TEXT   BODY[]

    #  BODY[] BODY.PEEK[HEADER] BODY.PEEK[1.MIME] BODY.PEEK[1] RFC822
    #query.add('BODY.PEEK[HEADER.FIELDS (SUBJECT)]')
    #print(client.capabilities)
    #print(client.scalix_id())
    print(client.namespace())

    for folder in client.folders():
        print(folder)

    folder = ImapFolder(b'Inbox', b'/', {})
    msg = list(client.messages(folder, query))[-1]
    pprint.pprint(dict(msg.dump()))
    pprint.pprint(msg.rfc822_size)
    pprint.pprint(msg.header_item('Message-ID'))
    #for msg in client.messages(folder, query):
    #    print(msg.uid, msg.sequence_id)
        #print(msg.envelope.subject)
        #print(msg.dump())
    #pprint(list())

