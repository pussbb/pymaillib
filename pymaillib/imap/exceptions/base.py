# -*- coding: utf-8 -*-
"""
    Imap4 exceptions
    ~~~~~~~~~~~~~~~~
    Imap4 exceptions

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""


class ImapClientException(Exception):
    """Base exception for the imap folder. All new Exception for pyimaplib
     module should subclass with this class.

    """
    pass


class ImapClientAbort(ImapClientException):
    """Common exception when server abort some operations

    """
    pass


class ImapByeByeException(ImapClientException):
    """Common exception when server abort some operations

    """
    pass

class ImapClientError(ImapClientException):
    """Common exception for an error.

    """
    pass


class ImapClientReadOnlyError(ImapClientException):
    """Exception indicates that opened mailbox at IMAP server in
    read-only mode and you can not add/update/delete anything.

    """
    pass


class ImapRuntimeError(ImapClientException, RuntimeError):
    """Generic runtime exception. Commonly used for unsuccessful requests to
     the sevrer.

    """
    pass


class ImapAuthorizationException(ImapClientException):
    """Could not authenticate user by name and password at this
    IMAP server.

    """
    pass


class ImapReferralsException(ImapAuthorizationException):
    """Referral exception raises when one server returns that user's mailbox
    at another server and client should go that server and authenticate user
    there. Have additional attribute `imap_url`.

    """

    def __init__(self, imap_url, message):
        self.imap_url = imap_url
        self.message = message
        super().__init__(message)


class ImapUnsupportedCommand(ImapClientException):
    """Helper Exception class. Unlikely you will see this exception it's for
     internal usage

    """

    def __init__(self, command):
        message = 'Server does not support command {}'.format(command)
        super().__init__(message)


class ImapIllegalStateException(ImapClientException):
    """Indicates that you can not use this connection because it was
     closed from client side or by the server.

    """
    pass


class ImapInvalidArgument(ImapRuntimeError):
    """Helper class maybe need to remove it

    """

    def __init__(self, name, value):
        message = 'Provided argument "{}"  value "{}" is invalid.'.format(
            name,
            value
        )
        super().__init__(message)


class ImapObjectNotFound(ImapRuntimeError):
    """Entity is not exists at IMAP server

    """
    pass


class ImapResponseParserError(ImapRuntimeError):
    """Parser related exceptions

    """
    pass
