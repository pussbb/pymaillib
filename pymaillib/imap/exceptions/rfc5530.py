# -*- coding: utf-8 -*-
"""
    Imap4 exceptions
    ~~~~~~~~~~~~~~~~
    Implementation of some IMAP response codes from RFC 5530 as Exceptions

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

from . import ImapClientException, ImapAuthorizationException


class ImapUnavailable(ImapClientException):
    """UNAVAILABLE
    Temporary failure because a subsystem is down.  For example, an
    IMAP server that uses a Lightweight Directory Access Protocol
    (LDAP) or Radius server for authentication might use this
    response code when the LDAP/Radius server is down.

    Example:
        C: a LOGIN "fred" "foo"
        S: a NO [UNAVAILABLE] User's backend down for maintenance

    """
    pass


class ImapAuthenticationFailed(ImapAuthorizationException):
    """AUTHENTICATIONFAILED
    Authentication failed for some reason on which the server is
    unwilling to elaborate.  Typically, this includes "unknown
    user" and "bad password".

    This is the same as not sending any response code, except that
    when a client sees AUTHENTICATIONFAILED, it knows that the
    problem wasn't, e.g., UNAVAILABLE, so there's no point in
    trying the same login/password again later.

    Example:
        C: b LOGIN "fred" "foo"
        S: b NO [AUTHENTICATIONFAILED] Authentication failed

    """
    pass


class ImapAuthorizationFailed(ImapAuthorizationException):
    """AUTHORIZATIONFAILED
    Authentication succeeded in using the authentication identity,
    but the server cannot or will not allow the authentication
    identity to act as the requested authorization identity.  This
    is only applicable when the authentication and authorization
    identities are different.

    Example:
        C: c1 AUTHENTICATE PLAIN
        [...]
        S: c1 NO [AUTHORIZATIONFAILED] No such authorization-ID

        C: c2 AUTHENTICATE PLAIN
        [...]
        S: c2 NO [AUTHORIZATIONFAILED] Authenticator is not an admin

    """
    pass


class ImapExpired(ImapAuthorizationException):
    """EXPIRED
    Either authentication succeeded or the server no longer had the
    necessary data; either way, access is no longer permitted using
    that passphrase.  The client or user should get a new passphrase.

    Example:
        C: d login "fred" "foo"
        S: d NO [EXPIRED] That password isn't valid any more

    """
    pass


class ImapPrivacyRequired(ImapClientException):
    """PRIVACYREQUIRED
    The operation is not permitted due to a lack of privacy.  If
    Transport Layer Security (TLS) is not in use, the client could
    try STARTTLS (see Section 6.2.1 of [RFC3501]) and then repeat
    the operation.

    Example:
        C: d login "fred" "foo"
        S: d NO [PRIVACYREQUIRED] Connection offers no privacy

        C: d select inbox
        S: d NO [PRIVACYREQUIRED] Connection offers no privacy

    """
    pass


class ImapContactAdmin(ImapClientException):
    """CONTACTADMIN
    The user should contact the system administrator or support desk.

    Example:
        C: e login "fred" "foo"
        S: e OK [CONTACTADMIN]

    """
    pass


class ImapNoPermit(ImapClientException):
    """NOPERM
    The access control system (e.g., Access Control List (ACL), see
    [RFC4314]) does not permit this user to carry out an operation,
    such as selecting or creating a mailbox.

    Example:
        C: f select "/archive/projects/experiment-iv"
        S: f NO [NOPERM] Access denied

    """
    pass


class ImapInUse(ImapClientException):
    """INUSE
    An operation has not been carried out because it involves
    sawing off a branch someone else is sitting on.  Someone else
    may be holding an exclusive lock needed for this operation, or
    the operation may involve deleting a resource someone else is
    using, typically a mailbox.

    The operation may succeed if the client tries again later.

    Example:
        C: g delete "/archive/projects/experiment-iv"
        S: g NO [INUSE] Mailbox in use

    """
    pass


class ImapExpungeIssued(ImapClientException):
    """EXPUNGEISSUED
    Someone else has issued an EXPUNGE for the same mailbox.  The
    client may want to issue NOOP soon.  [RFC2180] discusses this
    subject in depth.

    Example:
        C: h search from fred@example.com
        S: * SEARCH 1 2 3 5 8 13 21 42
        S: h OK [EXPUNGEISSUED] Search completed

    """
    pass


class ImapCorruption(ImapClientException):
    """CORRUPTION
    The server discovered that some relevant data (e.g., the
    mailbox) are corrupt.  This response code does not include any
    information about what's corrupt, but the server can write that
    to its logfiles.

    Example:
        C: i select "/archive/projects/experiment-iv"
        S: i NO [CORRUPTION] Cannot open mailbox

    """
    pass


class ImapServerBug(ImapClientException):
    """SERVERBUG
    The server encountered a bug in itself or violated one of its
    own invariants.

    Example:
        C: j select "/archive/projects/experiment-iv"
        S: j NO [SERVERBUG] This should not happen

    """
    pass


class ImapClientBug(ImapClientException):
    """CLIENTBUG
    The server has detected a client bug.  This can accompany all
    of OK, NO, and BAD, depending on what the client bug is.

    Example:
        C: k1 select "/archive/projects/experiment-iv"
        [...]
        S: k1 OK [READ-ONLY] Done
        C: k2 status "/archive/projects/experiment-iv" (messages)
        [...]
        S: k2 OK [CLIENTBUG] Done

    """
    pass


class ImapCannot(ImapClientException):
    """CANNOT
    The operation violates some invariant of the server and can
    never succeed.

    Example:
        C: l create "///////"
        S: l NO [CANNOT] Adjacent slashes are not supported

    """
    pass


class ImapLimit(ImapClientException):
    """LIMIT
    The operation ran up against an implementation limit of some
    kind, such as the number of flags on a single message or the
    number of flags used in a mailbox.

    Example:
        C: m STORE 42 FLAGS f1 f2 f3 f4 f5 ... f250
        S: m NO [LIMIT] At most 32 flags in one mailbox supported

    """
    pass


class ImapOverQuota(ImapClientException):
    """OVERQUOTA
    The user would be over quota after the operation.  (The user
    may or may not be over quota already.)

    Note that if the server sends OVERQUOTA but doesn't support the
    IMAP QUOTA extension defined by [RFC2087], then there is a
    quota, but the client cannot find out what the quota is.

    Example:
        C: n1 uid copy 1:* oldmail
        S: n1 NO [OVERQUOTA] Sorry

        C: n2 uid copy 1:* oldmail
        S: n2 OK [OVERQUOTA] You are now over your soft quota
    """
    pass


class ImapAlreadyExists(ImapClientException):
    """ALREADYEXISTS
    The operation attempts to create something that already exists,
    such as when the CREATE or RENAME directories attempt to create
    a mailbox and there is already one of that name.

    Example:
        C: o RENAME this that
        S: o NO [ALREADYEXISTS] Mailbox "that" already exists

    """
    pass


class ImapNoneExistent(ImapClientException):
    """NONEXISTENT
    The operation attempts to delete something that does not exist.
    Similar to ALREADYEXISTS.

    Example:
        C: p RENAME this that
        S: p NO [NONEXISTENT] No such mailbox
    """
    pass


RFC5530 = {
    'UNAVAILABLE': ImapUnavailable,
    'AUTHENTICATIONFAILED': ImapAuthenticationFailed,
    'AUTHORIZATIONFAILED': ImapAuthorizationFailed,
    'EXPIRED': ImapExpired,
    'PRIVACYREQUIRED': ImapPrivacyRequired,
    'CONTACTADMIN': ImapContactAdmin,
    'NOPERM': ImapNoPermit,
    'INUSE': ImapInUse,
    'EXPUNGEISSUED': ImapExpungeIssued,
    'CORRUPTION': ImapCorruption,
    'SERVERBUG': ImapServerBug,
    'CLIENTBUG': ImapClientBug,
    'CANNOT': ImapCannot,
    'LIMIT': ImapLimit,
    'OVERQUOTA': ImapOverQuota,
    'ALREADYEXISTS': ImapAlreadyExists,
    'NONEXISTENT': ImapNoneExistent,
}
