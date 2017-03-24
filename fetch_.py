# -*- coding: utf-8 -*-
"""

"""
import imaplib
import pprint



from pymaillib.imap.entity.folder import ImapFolder
from pymaillib.mailbox import UserMailbox
from pymaillib.imap.fetch_query_builder import FetchQueryBuilder

imaplib.Debug = 0


mailbox = UserMailbox('sxadmin', '1')
# time.sleep(1)

with mailbox.imap() as client:
    query = FetchQueryBuilder.fast(sequence='1:*')
#RFC822.HEADER RFC822.TEXT   BODY[]

    #  BODY[] BODY.PEEK[HEADER] BODY.PEEK[1.MIME] BODY.PEEK[1] RFC822
    #query.add('BODY.PEEK[HEADER.FIELDS (SUBJECT)]')
    query.fetch_envelope()
    query.fetch_body_peek()
    #query.add('BODY.PEEK[]')
    print(query)

    raise SystemExit
    for folder in client.folders():
        print(folder)

    folder = ImapFolder(b'Inbox', b'/', {})
    pprint.pprint(len(list(client.messages(folder, query))))
    #for msg in client.messages(folder, query):
    #    print(msg.uid, msg.sequence_id)
        #print(msg.envelope.subject)
        #print(msg.dump())
    #pprint(list())

