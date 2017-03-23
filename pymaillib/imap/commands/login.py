# -*- coding: utf-8 -*-
"""
    Imap4 Login Command
    ~~~~~~~~~~~~~~~~
    Executes IMAP Login command to authorize user at imap server

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
import re

from . import ImapBaseCommand
from ..exceptions import ImapAuthorizationException, ImapClientError,\
    ImapReferralsException

_MATCH_URL_RE = re.compile(rb'\[REFERRAL\s(?P<url>.*)\]\s(?P<message>.*)')


class ImapLoginCommand(ImapBaseCommand):
    """Authorize user at imap server

    """

    _COMMAND = 'LOGIN'

    def __init__(self, auth_data):
        self.auth_data = auth_data

    def run(self, imap_obj):
        """
         imap_obj.login could not raise exception during auth if REFERRAL
         exist on server response.
         REFERRAL server response example:
          This server is down, try another one.
          1) OK [REFERRAL imap://testuser1@test.com;AUTH=PLAIN@64.186.18.200/]
          This server is down, try another one.
          1) NO [REFERRAL imap://testuser1@test.com;AUTH=PLAIN@64.186.18.200/]

          If wrong credentials were sent to server, Dovecot return:
               b'[AUTHENTICATIONFAILED] Authentication failed.'
          If wrong credentials were sent to server, Scalix return:
               b'LOGIN failure, user name or password rejected'
        :param imap_obj:
        :return:
        """
        try:
            typ, data = imap_obj.login(
                self.auth_data.username,
                str(self.auth_data.password)
            )

            self.check_refferal(self.tagged_message(data))
            #  some servers can send updated CAPABILITY response
            #  as part of a successful authentication
            return self.untagged_value(imap_obj, 'CAPABILITY', b'').split(b' ')

        except ImapReferralsException as _:
            raise
        except ImapClientError as exception:
            self.check_refferal(exception.args[0])
            raise ImapAuthorizationException(exception)

    def check_refferal(self, data):
        """Check if response message contains imap url

        Raises:
            - ImapReferralsException when returned data contains imap url
            it means that client must reestablish connection to the
            provided imap url

        :param data:
        :return:
        """

        match = _MATCH_URL_RE.match(data)
        if match:
            raise ImapReferralsException(match.group('url'),
                                         match.group('message'))
