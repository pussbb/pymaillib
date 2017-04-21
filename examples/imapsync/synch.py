# -*- coding: utf-8 -*-
"""

"""
import concurrent.futures
import warnings
from pprint import pprint
from typing import List, Tuple, Dict

from pymaillib.imap.query.builders.store import StoreQueryBuilder
from pymaillib.imap.entity.email_message import ImapFetchedItem
from pymaillib.imap.query.builders.fetch import FetchQueryBuilder
from pymaillib.imap.client import ImapClient, ImapFolder
from pymaillib.imap.entity.server import ImapNamespace, Namespaces
from pymaillib.mailbox import UserMailbox
from pymaillib.settings import Config

#imaplib.Debug = 55
from_config = Config().from_config_file('./from_server.ini')

from_mailbox = UserMailbox('sxadmin', '1', from_config)

to_config = Config().from_config_file('./to_server.ini')

to_mailbox = UserMailbox('migrate', '123456', from_config)


def get_folders(namespace: ImapNamespace, imap: ImapClient) -> List[ImapFolder]:
    """
    
    :param namespace: 
    :param imap: 
    :return: 
    """
    res = []
    for _namespace in namespace:
        if _namespace.name:
            print(_namespace)
            res.append(ImapFolder(_namespace.name.strip('/'),
                                  _namespace.separator, {b'\\Noselect': b''}))
        res.extend(imap.folders(namespace=_namespace))
    return res


def get_user_folders(namespaces: Namespaces, imap: ImapClient) -> \
        Tuple[List[str], Dict[str, ImapFolder]]:
    """
    
    :param namespaces: 
    :param imap: 
    :return: 
    """
    folders = {}
    public_folders = []
    for namespace in [namespaces.public_folders, namespaces.other_users]:
        for folder_ in get_folders(namespace, imap):
            public_folders.append(folder_.name)

    for folder_ in get_folders(namespaces.private, imap):
        if folder_.name in public_folders:
            continue
        folders[folder_.name] = folder_
    return public_folders, folders

from_folders = []
from_public_folders = []
with from_mailbox.imap() as imap:
    from_public_folders, from_folders = get_user_folders(imap.namespace(), imap)

print('Skipped following not private folders')
pprint(from_public_folders)

print('Private folders in server migrating from is:')
pprint(list(from_folders))

to_folders = []
to_public_folders = []
with to_mailbox.imap() as imap:
    to_public_folders, to_folders = get_user_folders(imap.namespace(), imap)

print('Skipped non private folders at destination server')
pprint(to_public_folders)

print('Private folders in destination server is:')
pprint(list(to_folders))

folder_diff = set(from_folders).difference(set(to_folders))

if folder_diff:
    print('Destination mailbox does not have such folders')
    pprint(folder_diff)
    print('Lets create them')
    with to_mailbox.imap() as imap:
        for folder_name in iter(folder_diff):
            folder = from_folders.get(folder_name)
            parent = folder.parent()
            top_level = []
            while parent:
                top_level.append(parent)
                parent = parent.parent()
            for top_folder in reversed(top_level):
                try:
                    folder_diff.remove(top_folder.name)
                except KeyError as _:
                    pass
                if top_folder.name not in to_folders:
                    imap.create_folder(top_folder.name, top_folder.parent())
            imap.create_folder(folder.name)


def get_folder_messages(folder:ImapFolder, imap:ImapClient) -> \
    List[ImapFetchedItem]:
    """
    
    :param folder: 
    :param imap: 
    :return: 
    """

    data = range(1, folder.total)
    n = 200  # by chunks
    res = {}
    for item in [data[i:i + n] for i in range(0, len(data), n)]:
        fp = FetchQueryBuilder(list(item)).fetch_envelope()
        for item in imap.fetch(fp):
            res[item.envelope.message_id] = item
    return res


def fill_mailbox(source_mailbox, dest_mailbox, folder):
    from_messages = {}
    with source_mailbox.imap() as imap:
        imap.update_folder_info(folder)
        from_messages = get_folder_messages(folder, imap)

    to_messages = {}
    with to_mailbox.imap() as imap:
        imap.update_folder_info(folder)
        to_messages = get_folder_messages(folder, imap)

    try:
        dest_mailbox.close()
    except Exception as _:
        pass

    msgs_diff = set(from_messages).difference(set(to_messages))
    count = 0
    for msg_id in msgs_diff:
        msg = from_messages.get(msg_id)
        if not msg:
            warnings.warn('Oopps not found {}'.format(msg_id), RuntimeWarning)
        with source_mailbox.imap() as imap:
            fp = FetchQueryBuilder(uids=msg.uid).fetch_body_structure() \
                .fetch_rfc822().fetch_flags()
            msg = list(imap.fetch(fp))[-1]

            rfc822 = msg.rfc822
            if not rfc822['X-Scalix-Class']:
                message_class = 'IPM.Note'
                for part in msg.bodystructure:
                    if part.content_part == 'text/calendar':
                        message_class = 'IPM.Appointment'
                        break
                rfc822.add_header('X-Scalix-Class', message_class)

            with dest_mailbox.imap() as imap2:
                imap2.select_folder(folder)
                new_msg = imap2.append_message(rfc822, folder)
                query = StoreQueryBuilder(uids=new_msg.uid)
                for flag in msg.flags:
                    query.add(flag)
                query.silent = True
                imap2.store(query)
            count += 1
    return count


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(fill_mailbox, from_mailbox.clone(),
                                     to_mailbox.clone(), folder): folder
                     for folder in from_folders.values()}
    for future in concurrent.futures.as_completed(future_to_url):
        folder = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('{} generated an exception: {}'.format(folder, exc))
        else:
            print('{} msgs synched {}'.format(folder, data))
