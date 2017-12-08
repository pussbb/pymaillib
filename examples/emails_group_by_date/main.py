# -*- coding: utf-8 -*-
"""

"""
from collections import defaultdict
from pprint import pprint
from typing import List

from pymaillib.imap.client import ImapClient
from pymaillib.imap.entity.email_message import ImapFetchedItem
from pymaillib.imap.entity.folder import ImapFolder
from pymaillib.imap.query.builders.fetch import FetchQueryBuilder
from pymaillib.mailbox import UserMailbox
from pymaillib.settings import Config

CONFIG = {
    'imap': {
        'host': 'HOST'
    }
}


def get_folder_messages(folder: ImapFolder, imap: ImapClient) -> \
        List[ImapFetchedItem]:
    """

    :param folder:
    :param imap:
    :return:
    """
    if not folder.total:
        raise StopIteration
    data = range(1, folder.total)
    n = 200  # by chunks

    for items in [data[i:i + n] for i in range(1, len(data), n)]:
        fp = FetchQueryBuilder(list(items)).fetch_envelope().fetch_uid()
        for email in imap.fetch(fp):
            yield email.uid, email.envelope.date


mailbox = UserMailbox('HOST', 'USER', Config(CONFIG))

with mailbox.imap() as imap_conn:
    folder = imap_conn.folder_by_name('Inbox')
    imap_conn.select_folder(folder)
    imap_conn.update_folder_info(folder)
    res = defaultdict(lambda: defaultdict(list))
    for uid, date in get_folder_messages(folder, imap_conn):
        if not date:
            continue
        res[date.year][date.month].append(uid)
    pprint(res, width=150, depth=2, compact=True)
