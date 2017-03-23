# -*- coding: utf-8 -*-
"""

"""

import weakref

import time

_id2obj_dict = weakref.WeakValueDictionary()

def remember(obj):
    oid = id(obj)
    _id2obj_dict[oid] = obj
    return oid

def id2obj(oid):
    return _id2obj_dict.get(oid)

class S(object):

    def __del__(self):
        print('dell')

s = S()
sid = id(s)
print(s, sid)
remember(s)
print(id2obj(sid))
while _id2obj_dict:
    _, o = _id2obj_dict.popitem()
    del o

print(list(_id2obj_dict.keys()))
time.sleep(1)
print('deleted', id2obj(sid))


raise SystemExit


class ImapFolder(object):
    pass


class ImapClient(object):
    pass

class ImapFolderClient(object):
    pass


class UserIMapPoolConnectionManager(object):

    __instances = weakref.WeakValueDictionary()

    def __init__(self, credentials):
        #  assuming that credentials auth_data: UserCredentials
        self.__credentials = credentials
        self.__connections = weakref.WeakValueDictionary()

    @staticmethod
    def get_instance(user):
        pool = UserIMapPoolConnectionManager.__instances.get(user)
        if not pool:
            pool = UserIMapPoolConnectionManager(user)
            UserIMapPoolConnectionManager.__instances[user] = pool
        return pool

    def get(self, id=None):
        conn = self.__conections.get(id)
        if conn is None:
            #if isinstance(id, ImapFolder):
            #    conn = self.__new_folder_imap_connection()
            conn = self.__new_imap_connection()
            self.__conections[id] = conn
        return conn

    def release(self, id):
        self.__close_connection(self.__conections.pop(id, None))

    def __close_connection(self, conn):
        if conn:
            conn.close()
            del conn

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        while self.__conections:
            self.__close_connection(self.__conections.popitem()[-1])

    @staticmethod
    def close(user):
        pool = UserIMapPoolConnectionManager.__instances.pop(user, None)
        if pool:
            pool.close()

    def __new_imap_connection(self):
        # with reirections etc
        return ImapClient(self.__credentials)


imap_pool = UserIMapPoolConnectionManager.get_instance({})
imap_pool.get() # auth
# ImapClient
# def select_folder()
#   pool = UserIMapPoolConnectionManager.get_instance(self.auth_data)
#   conn = pool.get(folder)
#   conn.sele



with imap_pool.get() as client:
    pass
