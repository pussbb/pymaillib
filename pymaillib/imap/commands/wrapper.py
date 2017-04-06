# -*- coding: utf-8 -*-
"""
    Dummy command to execute imaplibImap4 functions and have the same 
    functionality
    ~~~~~~~~~~~~~~~~
   
   
    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import imaplib

from imap.commands import ImapBaseCommand


class ImapLibWrapper(ImapBaseCommand):

    name = "IMAP4"

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self, imap_obj: imaplib.IMAP4):
        typ, data = getattr(imap_obj, self.func)(*self.args, **self.kwargs)
        self.check_response(typ, data)
        return data
