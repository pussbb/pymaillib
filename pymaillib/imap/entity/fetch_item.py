# -*- coding: utf-8 -*-
"""
    Imap Fetch Item
    ~~~~~~~~~~~~~~~~
    Imap Fetch Item

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from ..utils import parse_datetime
from .body_structure import BodyStructure
from .envelope import Envelope

FETCH_ITEMS = {}
__all__ = ['FETCH_ITEMS']


class FetchItem(object):
    """Class that represents message items used in Imap FETCH request
        see https://tools.ietf.org/html/rfc3501#section-6.4.5
    """

    __slots__ = ('_part', '_size')

    name = None
    allow_part = False
    partial = False

    def __init__(self):
        self._size = 0
        self._part = ''

    @property
    def part(self):
        """Some atom_data items gives ability to get from the server specific part
        for e.g. BODY.PEEK[0] or BODY.PEEK["text/plain"]

        :return:
        """
        if self._part is None:
            return ''
        return self._part

    @part.setter
    def part(self, value):
        """ Sets what part of item is extract from the imap server

        :param value:
        :return:
        """
        if not self.allow_part:
            raise RuntimeError('Not supported by this atom')
        self._part = value

    @property
    def size(self):
        """Size of atom_data to extract from the server

        :return:
        """
        return self._size

    @size.setter
    def size(self, value):
        """Set size of atom_data which need to get from the server.

        :param value:
        :return:
        """
        if not self.partial:
            raise RuntimeError('Not supported by this atom')
        self._size = value

    def __repr__(self):
        res = [self.name.decode()]
        if self.allow_part:
            res.extend(['[', str(self.part), ']'])
        if self.partial and self._size:
            res.extend(['<', str(self._size), '>'])
        return ''.join(res)

    @staticmethod
    def parse(atom_data, value):
        """Abstract method all sub classes must implement them
            see https://tools.ietf.org/html/rfc3501#page-73

        :param atom_data: dict
        :param value: bytes
        :return:
        """
        raise NotImplementedError


class UIDFetchItem(FetchItem):
    """UID
         The unique identifier for the message.

    """

    __slots__ = ()

    name = rb'UID'

    @staticmethod
    def parse(atom_data, value):
        """ A number expressing the unique identifier of the message.

        :param atom_data: bytes
        :param value: bytes or None
        :return: int or None
        """
        return value


class BodyFetchItem(FetchItem):
    """BODY[<section>]<<partial>>
    The text of a particular body section.  The section
    specification is a set of zero or more part specifiers
    delimited by periods.  A part specifier is either a part number
    or one of the following: HEADER, HEADER.FIELDS,
    HEADER.FIELDS.NOT, MIME, and TEXT.  An empty section
    specification refers to the entire message, including the
    header.

    Every message has at least one part number.  Non-[MIME-IMB]
    messages, and non-multipart [MIME-IMB] messages with no
    encapsulated message, only have a part 1.

    Multipart messages are assigned consecutive part numbers, as
    they occur in the message.  If a particular part is of type
    message or multipart, its parts MUST be indicated by a period
    followed by the part number within that nested multipart part.

    A part of type MESSAGE/RFC822 also has nested part numbers,
    referring to parts of the MESSAGE part's body.

    The HEADER, HEADER.FIELDS, HEADER.FIELDS.NOT, and TEXT part
    specifiers can be the sole part specifier or can be prefixed by
    one or more numeric part specifiers, provided that the numeric
    part specifier refers to a part of type MESSAGE/RFC822.  The
    MIME part specifier MUST be prefixed by one or more numeric
    part specifiers.

    The HEADER, HEADER.FIELDS, and HEADER.FIELDS.NOT part
    specifiers refer to the [RFC-2822] header of the message or of
    an encapsulated [MIME-IMT] MESSAGE/RFC822 message.
    HEADER.FIELDS and HEADER.FIELDS.NOT are followed by a list of
    field-name (as defined in [RFC-2822]) names, and return a
    subset of the header.  The subset returned by HEADER.FIELDS
    contains only those header fields with a field-name that
    matches one of the names in the list; similarly, the subset
    returned by HEADER.FIELDS.NOT contains only the header fields
    with a non-matching field-name.  The field-matching is
    case-insensitive but otherwise exact.  Subsetting does not
    exclude the [RFC-2822] delimiting blank line between the header
    and the body; the blank line is included in all header fetches,
    except in the case of a message which has no body and no blank
    line.

    The MIME part specifier refers to the [MIME-IMB] header for
    this part.

    The TEXT part specifier refers to the text body of the message,
    omitting the [RFC-2822] header.

    Here is an example of a complex message with some of its
    part specifiers:

        HEADER     ([RFC-2822] header of the message)
        TEXT       ([RFC-2822] text body of the message) MULTIPART/MIXED
        1          TEXT/PLAIN
        2          APPLICATION/OCTET-STREAM
        3          MESSAGE/RFC822
        3.HEADER   ([RFC-2822] header of the message)
        3.TEXT     ([RFC-2822] text body of the message) MULTIPART/MIXED
        3.1        TEXT/PLAIN
        3.2        APPLICATION/OCTET-STREAM
        4          MULTIPART/MIXED
        4.1        IMAGE/GIF
        4.1.MIME   ([MIME-IMB] header for the IMAGE/GIF)
        4.2        MESSAGE/RFC822
        4.2.HEADER ([RFC-2822] header of the message)
        4.2.TEXT   ([RFC-2822] text body of the message) MULTIPART/MIXED
        4.2.1      TEXT/PLAIN
        4.2.2      MULTIPART/ALTERNATIVE
        4.2.2.1    TEXT/PLAIN
        4.2.2.2    TEXT/RICHTEXT


    It is possible to fetch a substring of the designated text.
    This is done by appending an open angle bracket ("<"), the
    octet position of the first desired octet, a period, the
    maximum number of octets desired, and a close angle bracket
    (">") to the part specifier.  If the starting octet is beyond
    the end of the text, an empty string is returned.

    Any partial fetch that attempts to read beyond the end of the
    text is truncated as appropriate.  A partial fetch that starts
    at octet 0 is returned as a partial fetch, even if this
    truncation happened.

    Note: This means that BODY[]<0.2048> of a 1500-octet message
    will return BODY[]<0> with a literal of size 1500, not
    BODY[].

    Note: A substring fetch of a HEADER.FIELDS or
    HEADER.FIELDS.NOT part specifier is calculated after
    subsetting the header.

    The \\Seen flag is implicitly set; if this causes the flags to
    change, they SHOULD be included as part of the FETCH responses.

    """

    __slots__ = ()

    name = rb'BODY'

    allow_part = True
    partial = True

    @staticmethod
    def parse(atom_data, value):
        """ BODY[<section>]<<origin octet>>
        A string expressing the body contents of the specified section.
        The string SHOULD be interpreted by the client according to the
        content transfer encoding, body type, and subtype.

        If the origin octet is specified, this string is a substring of
        the entire body contents, starting at that origin octet.  This
        means that BODY[]<0> MAY be truncated, but BODY[] is NEVER
        truncated.

           Note: The origin octet facility MUST NOT be used by a server
           in a FETCH response unless the client specifically requested
           it by means of a FETCH of a BODY[<section>]<<partial>> atom_data
           item.

        8-bit textual atom_data is permitted if a [CHARSET] identifier is
        part of the body parameter parenthesized list for this section.
        Note that headers (part specifiers HEADER or MIME, or the
        header portion of a MESSAGE/RFC822 part), MUST be 7-bit; 8-bit
        characters are not permitted in headers.  Note also that the
        [RFC-2822] delimiting blank line between the header and the
        body is not affected by header line subsetting; the blank line
        is always included as part of header atom_data, except in the case
        of a message which has no body and no blank line.

        Non-textual atom_data such as binary atom_data MUST be transfer encoded
        into a textual form, such as BASE64, prior to being sent to the
        client.  To derive the original binary atom_data, the client MUST
        decode the transfer encoded string.

        :param value: bytes
        :param atom_data: bytes

   """
        if atom_data.get('part') is None:
            return {
                'BODYSTRUCTURE': BodyStructureFetchItem.parse(atom_data, value)
            }

        part = atom_data.get('part').decode()
        if not part:
            part = 0
        return {part: value}


class BodyStructureFetchItem(FetchItem):
    """BODYSTRUCTURE
         The [MIME-IMB] body structure of the message.  This is computed
         by the server by parsing the [MIME-IMB] header fields in the
         [RFC-2822] header and [MIME-IMB] headers.

    """

    __slots__ = ()

    name = rb'BODYSTRUCTURE'

    @staticmethod
    def parse(atom_data, value):
        """BODYSTRUCTURE
         A parenthesized list that describes the [MIME-IMB] body
         structure of a message.  This is computed by the server by
         parsing the [MIME-IMB] header fields, defaulting various fields
         as necessary.

         For example, a simple text message of 48 lines and 2279 octets
         can have a body structure of: ("TEXT" "PLAIN" ("CHARSET"
         "US-ASCII") NIL NIL "7BIT" 2279 48)

         Multiple parts are indicated by parenthesis nesting.  Instead
         of a body type as the first element of the parenthesized list,
         there is a sequence of one or more nested body structures.  The
         second element of the parenthesized list is the multipart
         subtype (mixed, digest, parallel, alternative, etc.).

         For example, a two part message consisting of a text and a
         BASE64-encoded text attachment can have a body structure of:
         (("TEXT" "PLAIN" ("CHARSET" "US-ASCII") NIL NIL "7BIT" 1152
         23)("TEXT" "PLAIN" ("CHARSET" "US-ASCII" "NAME" "cc.diff")
         "<960723163407.20117h@cac.washington.edu>" "Compiler diff"
         "BASE64" 4554 73) "MIXED")

         Extension atom_data follows the multipart subtype.  Extension atom_data
         is never returned with the BODY fetch, but can be returned with
         a BODYSTRUCTURE fetch.  Extension atom_data, if present, MUST be in
         the defined order.  The extension atom_data of a multipart body part
         are in the following order:

         body parameter parenthesized list
            A parenthesized list of attribute/value pairs [e.g., ("foo"
            "bar" "baz" "rag") where "bar" is the value of "foo", and
            "rag" is the value of "baz"] as defined in [MIME-IMB].

         body disposition
            A parenthesized list, consisting of a disposition type
            string, followed by a parenthesized list of disposition
            attribute/value pairs as defined in [DISPOSITION].

         body language
            A string or parenthesized list giving the body language
            value as defined in [LANGUAGE-TAGS].

         body location
            A string list giving the body content URI as defined in
            [LOCATION].

         Any following extension atom_data are not yet defined in this
         version of the protocol.  Such extension atom_data can consist of
         zero or more NILs, strings, numbers, or potentially nested
         parenthesized lists of such atom_data.  Client implementations that
         do a BODYSTRUCTURE fetch MUST be prepared to accept such
         extension atom_data.  Server implementations MUST NOT send such
         extension atom_data until it has been defined by a revision of this
         protocol.

         The basic fields of a non-multipart body part are in the
         following order:

         body type
            A string giving the content media type name as defined in
            [MIME-IMB].

         body subtype
            A string giving the content subtype name as defined in
            [MIME-IMB].

         body parameter parenthesized list
            A parenthesized list of attribute/value pairs [e.g., ("foo"
            "bar" "baz" "rag") where "bar" is the value of "foo" and
            "rag" is the value of "baz"] as defined in [MIME-IMB].

         body id
            A string giving the content id as defined in [MIME-IMB].

         body description
            A string giving the content description as defined in
            [MIME-IMB].

         body encoding
            A string giving the content transfer encoding as defined in
            [MIME-IMB].

         body size
            A number giving the size of the body in octets.  Note that
            this size is the size in its transfer encoding and not the
            resulting size after any decoding.

         A body type of type MESSAGE and subtype RFC822 contains,
         immediately after the basic fields, the envelope structure,
         body structure, and size in text lines of the encapsulated
         message.

         A body type of type TEXT contains, immediately after the basic
         fields, the size of the body in text lines.  Note that this
         size is the size in its content transfer encoding and not the
         resulting size after any decoding.

         Extension atom_data follows the basic fields and the type-specific
         fields listed above.  Extension atom_data is never returned with the
         BODY fetch, but can be returned with a BODYSTRUCTURE fetch.
         Extension atom_data, if present, MUST be in the defined order.

         The extension atom_data of a non-multipart body part are in the
         following order:

         body MD5
            A string giving the body MD5 value as defined in [MD5].

         body disposition
            A parenthesized list with the same content and function as
            the body disposition for a multipart body part.

         body language
            A string or parenthesized list giving the body language
            value as defined in [LANGUAGE-TAGS].

         body location
            A string list giving the body content URI as defined in
            [LOCATION].

         Any following extension atom_data are not yet defined in this
         version of the protocol, and would be as described above under
         multipart extension atom_data.

        :param atom_data:
        :param value:
        :return:
        """
        return BodyStructure.build(value)


class BodyPeekFetchItem(BodyFetchItem):
    """BODY.PEEK[<section>]<<partial>>
         An alternate form of BODY[<section>] that does not implicitly
         set the \Seen flag.

    """

    __slots__ = ()

    name = rb'BODY.PEEK'


class EnvelopeFetchItem(FetchItem):
    """ENVELOPE
         The envelope structure of the message.  This is computed by the
         server by parsing the [RFC-2822] header into the component
         parts, defaulting various fields as necessary.

    """

    __slots__ = ()

    name = rb'ENVELOPE'

    @staticmethod
    def parse(atom_data, value):
        """ENVELOPE
        A parenthesized list that describes the envelope structure of a
        message.  This is computed by the server by parsing the
        [RFC-2822] header into the component parts, defaulting various
        fields as necessary.

        The fields of the envelope structure are in the following
        order: date, subject, from, sender, reply-to, to, cc, bcc,
        in-reply-to, and message-id.  The date, subject, in-reply-to,
        and message-id fields are strings.  The from, sender, reply-to,
        to, cc, and bcc fields are parenthesized lists of address
        structures.

        An address structure is a parenthesized list that describes an
        electronic mail address.  The fields of an address structure
        are in the following order: personal name, [SMTP]
        at-domain-list (source route), mailbox name, and host name.

        [RFC-2822] group syntax is indicated by a special form of
        address structure in which the host name field is NIL.  If the
        mailbox name field is also NIL, this is an end of group marker
        (semi-colon in RFC 822 syntax).  If the mailbox name field is
        non-NIL, this is a start of group marker, and the mailbox name
        field holds the group name phrase.

        If the Date, Subject, In-Reply-To, and Message-ID header lines
        are absent in the [RFC-2822] header, the corresponding member
        of the envelope is NIL; if these header lines are present but
        empty the corresponding member of the envelope is the empty
        string.

        Note: some servers may return a NIL envelope member in the
        "present but empty" case.  Clients SHOULD treat NIL and
        empty string as identical.

        Note: [RFC-2822] requires that all messages have a valid
        Date header.  Therefore, the date member in the envelope can
        not be NIL or the empty string.

        Note: [RFC-2822] requires that the In-Reply-To and
        Message-ID headers, if present, have non-empty content.
        Therefore, the in-reply-to and message-id members in the
        envelope can not be the empty string.

        If the From, To, cc, and bcc header lines are absent in the
        [RFC-2822] header, or are present but empty, the corresponding
        member of the envelope is NIL.

        If the Sender or Reply-To lines are absent in the [RFC-2822]
        header, or are present but empty, the server sets the
        corresponding member of the envelope to be the same value as
        the from member (the client is not expected to know to do
        this).

        Note: [RFC-2822] requires that all messages have a valid
        From header.  Therefore, the from, sender, and reply-to
        members in the envelope can not be NIL.

        :param atom_data:
        :param value:
        :return:
        """
        return Envelope.from_list(value)


class FlagsFetchItem(FetchItem):
    """FLAGS
         The flags that are set for this message.

    """
    __slots__ = ()

    name = rb'FLAGS'

    @staticmethod
    def parse(atom_data, value):
        """FLAGS
         A parenthesized list of flags that are set for this message.

        :param atom_data:
        :param value:
        :return:
        """
        return value


class IternalDateFetchItem(FetchItem):
    """INTERNALDATE
         The internal date of the message.

    """
    __slots__ = ()

    name = rb'INTERNALDATE'

    @staticmethod
    def parse(atom_data, value):
        """INTERNALDATE
         A string representing the internal date of the message.

        :param atom_data:
        :param value:
        :return:
        """
        try:
            return parse_datetime(value)
        except ValueError as exp:
            raise ValueError('{}: {}'.format(exp.args[0], atom_data))


class RFC822FetchItem(FetchItem):
    """ RFC822
         Functionally equivalent to BODY[], differing in the syntax of
         the resulting untagged FETCH atom_data (RFC822 is returned).

    """
    __slots__ = ()

    name = rb'RFC822'
    allow_part = False
    partial = False

    @staticmethod
    def parse(atom_data, value):
        """

        :param atom_data:
        :param value:
        :return:
        """
        return value


class RFC822HeaderFetchItem(RFC822FetchItem):
    """ RFC822.HEADER
         Functionally equivalent to BODY.PEEK[HEADER], differing in the
         syntax of the resulting untagged FETCH atom_data (RFC822.HEADER is
         returned).

    """
    __slots__ = ()

    name = rb'RFC822.HEADER'


class RFC822SizeFetchItem(UIDFetchItem):
    """ RFC822.SIZE
         The [RFC-2822] size of the message.

    """
    __slots__ = ()

    name = rb'RFC822.SIZE'


class RFC822TextFetchItem(RFC822FetchItem):
    """ RFC822.TEXT
         Functionally equivalent to BODY[TEXT], differing in the syntax
         of the resulting untagged FETCH atom_data (RFC822.TEXT is returned).

    """
    __slots__ = ()

    name = rb'RFC822.TEXT'


class XCutomFetchItem(FetchItem):
    """Handle Custom atoms in fetch response

    """

    name = rb'X-'

    @staticmethod
    def parse(atom_data, value):
        """

        :param atom_data:
        :param value:
        :return:
        """
        return atom_data, value


def __find_fetch_items():
    """find all classes which represents IMAP FETCH message part and
    put them into list of available items

    :return:
    """
    for name, obj in globals().items():
        try:
            if issubclass(obj, FetchItem):
                if obj.name:
                    FETCH_ITEMS.setdefault(obj.name, obj)
                __all__.append(name)
        except TypeError as _:
            pass

__find_fetch_items()
del __find_fetch_items
