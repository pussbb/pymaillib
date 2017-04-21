# -*- coding: utf-8 -*-
"""

"""
import imaplib
import pprint

from pymaillib.imap.query.builders.search import SearchQueryBuilder
from pymaillib.imap.entity.folder import ImapFolder
from pymaillib.imap.query.builders.store import StoreQueryBuilder
from pymaillib.imap.query.builders.fetch import FetchQueryBuilder
from pymaillib.mailbox import UserMailbox
from pymaillib.settings import Config

imaplib.Debug = 0


fetch_query = FetchQueryBuilder.fast('1')\
    .fetch_envelope()\
    .fetch_body_structure()\
    .fetch_rfc822_size()\
    .fetch_header_item('Subject')\
    .fetch_header_item('Message-ID')
# 1 (ENVELOPE INTERNALDATE RFC822.SIZE BODYSTRUCTURE UID FLAGS BODY[HEADER.FIELDS (Subject Message-ID)])
print(fetch_query)


config = Config().from_config_file('./pymail.ini')

mailbox = UserMailbox('sxadmin', '1', config)

with mailbox.imap() as client:
    with client as client2:
        # {'other_users': [{'separator': b'Other Users/', 'name': b'/'}],
        #  'public_folders': [{'separator': b'Public Folders/', 'name': b'/'}],
        # 'private': [{'separator': b'', 'name': b'/'}]}
        print(client2.namespace())

    for folder in client.folders():
        # Name:INBOX Path: / Attributes:{b'\\X-Unseen-Msgs': b'0',
        # b'\\X-Total-Msgs': b'19161', b'\\X-ModDate': b'20170407112206',
        # ....
        print(folder)
        print(folder.selectable)

    # [None]
    print(client.recent())

    folder = ImapFolder(b'Inbox', b'/', {})

    store_query = StoreQueryBuilder(1).remove(r'\SEEN')
    client.select_folder(folder)
    res = client.store(store_query)
    # [{'SEQ': 1, 'FLAGS': [b'\\Recent']}]
    print(list(res))
    search_query = SearchQueryBuilder()\
        .unseen()
    res = client.search(search_query)
    # [1]
    print(list(res))

    msg = list(client.fetch(folder, fetch_query))[-1]
    # {'BODY': {},
    # 'BODYSTRUCTURE': [{'disposition': None, 'boundary': ...
    # 'ENVELOPE': {'cc': [], 'message_id': b'<1991954822.314JavaMail....
    # 'FLAGS': [b'\\Seen', b'\\Recent'],
    # 'HEADER': {'Message-ID': '<1991954822.3148>', 'Subject': 'ewdew'},
    # 'INTERNALDATE': datetime.datetime(2017, 2, 6, ....,
    # 'RFC822.SIZE': 1020,
    # 'SEQ': 1,
    # 'UID': 1}
    pprint.pprint(dict(msg.dump()))
    # 1020
    pprint.pprint(msg.envelope)
    # '<1991954822.31486384534092.JavaMail.root@test.centosx64.com>'
    pprint.pprint(msg.header_item('Message-ID'))
