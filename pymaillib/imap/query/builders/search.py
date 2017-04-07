# -*- coding: utf-8 -*-
"""
    Imap4 Store Query Builder
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""
from typing import Tuple

from ...utils import escape_string, get_date
from . import BaseQueryBuilder, build_sequence


class SearchQueryBuilder(BaseQueryBuilder):
    """Creates search query
    """

    def __init__(self, *args, **kwargs):
        kwargs['requires_msg_set'] = False
        super().__init__(*args, **kwargs)
        self.__items = set()

    def add(self, item: str) -> 'SearchQueryBuilder':
        """Add custom search field
        :param item: string
        :return: SearchQueryBuilder
        """
        self.__items.add(str(item))
        return self

    def all(self) -> 'SearchQueryBuilder':
        """ All messages in the mailbox; the default initial key for
         ANDing.
        :return: SearchQueryBuilderSearchQueryBuilder
        """
        self.__items.add('ALL')
        return self

    def answered(self) -> 'SearchQueryBuilder':
        """ANSWERED
         Messages with the \Answered flag set.
        :return: SearchQueryBuilderSearchQueryBuilder
        """
        self.__items.add('ANSWERED')
        return self

    def bcc(self, value: str) -> 'SearchQueryBuilder':
        """ BCC <string>
         Messages that contain the specified string in the envelope
         structure's BCC field.
        :param value: value to search
        :return: SearchQueryBuilder
        """

        self.__items.add('BCC {}'.format(escape_string(value)))
        return self

    def before(self, value) -> 'SearchQueryBuilder':
        """      BEFORE <date>
         Messages whose internal date (disregarding time and timezone)
         is earlier than the specified date.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('BEFORE {}'.format(get_date(value)))
        return self

    def body(self, value) -> 'SearchQueryBuilder':
        """BODY <string>
         Messages that contain the specified string in the body of the
         message.
        :param value:
        :return: SearchQueryBuilderSearchQueryBuilder
        """
        self.__items.add('BODY {}'.format(escape_string(value)))
        return self

    def cc(self, value) -> 'SearchQueryBuilder':
        """CC <string>
         Messages that contain the specified string in the envelope
         structure's CC field.
        :param value:
        :return: SearchQueryBuilderSearchQueryBuilder
        """
        self.__items.add('CC {}'.format(escape_string(value)))
        return self

    def deleted(self) -> 'SearchQueryBuilder':
        """DELETED
         Messages with the \Deleted flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('DELETED')
        return self

    def draft(self) -> 'SearchQueryBuilder':
        """DRAFT
         Messages with the \Draft flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('DRAFT')
        return self

    def flagged(self) -> 'SearchQueryBuilder':
        """FLAGGED
        Messages with the \Flagged flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('FLAGGED')
        return self

    def from_(self, value) -> 'SearchQueryBuilder':
        """FROM <string>
        Messages that contain the specified string in the envelope
        structure's FROM field.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('FROM {}'.format(escape_string(value)))
        return self

    def header(self, header, value) -> 'SearchQueryBuilder':
        """HEADER <field-name> <string>
         Messages that have a header with the specified field-name (as
         defined in [RFC-2822]) and that contains the specified string
         in the text of the header (what comes after the colon).  If the
         string to search is zero-length, this matches all messages that
         have a header line with the specified field-name regardless of
         the contents.
        :param header:
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('HEADER {} {}'.format(header, escape_string(value)))
        return self

    def keyword(self, value) -> 'SearchQueryBuilder':
        """ KEYWORD <flag>
         Messages with the specified keyword flag set.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('KEYWORD {}'.format(str(value)))
        return self

    def larger(self, value) -> 'SearchQueryBuilder':
        """LARGER <n>
         Messages with an [RFC-2822] size larger than the specified
         number of octets.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('LARGER {}'.format(int(value)))
        return self

    def new(self) -> 'SearchQueryBuilder':
        """NEW
         Messages that have the \Recent flag set but not the \Seen flag.
         This is functionally equivalent to "(RECENT UNSEEN)".
        :return: SearchQueryBuilder
        """
        self.__items.add('NEW')
        return self

    def not_(self, value) -> 'SearchQueryBuilder':
        """NOT <search-key>
         Messages that do not match the specified search key.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('NOT {}'.format(escape_string(value)))
        return self

    def old(self) -> 'SearchQueryBuilder':
        """ OLD
         Messages that do not have the \Recent flag set.  This is
         functionally equivalent to "NOT RECENT" (as opposed to "NOT
         NEW").
        :return: SearchQueryBuilder
        """
        self.__items.add('OLD')
        return self

    def on(self, value) -> 'SearchQueryBuilder':
        """ON <date>
         Messages whose internal date (disregarding time and timezone)
         is within the specified date.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('ON {}'.format(get_date(value)))
        return self

    def or_(self, *args) -> 'SearchQueryBuilder':
        """OR <search-key1> <search-key2>
         Messages that match either search key.
        :return: SearchQueryBuilder
        """
        self.__items.add('OR {}'.format(
            ' '.join([escape_string(item) for item in args])
        ))
        return self

    def recent(self) -> 'SearchQueryBuilder':
        """RECENT
         Messages that have the \Recent flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('RECENT')
        return self

    def seen(self) -> 'SearchQueryBuilder':
        """SEEN
         Messages that have the \Seen flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('SEEN')
        return self

    def sent_before(self, value) -> 'SearchQueryBuilder':
        """SENTBEFORE <date>
         Messages whose [RFC-2822] Date: header (disregarding time and
         timezone) is earlier than the specified date.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('SENTBEFORE {}'.format(get_date(value)))
        return self

    def sent_on(self, value) -> 'SearchQueryBuilder':
        """SENTON <date>
         Messages whose [RFC-2822] Date: header (disregarding time and
         timezone) is within the specified date.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('SENTON {}'.format(get_date(value)))
        return self

    def sent_since(self, value) -> 'SearchQueryBuilder':
        """SENTSINCE <date>
         Messages whose [RFC-2822] Date: header (disregarding time and
         timezone) is within or later than the specified date.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('SENTSINCE {}'.format(get_date(value)))
        return self

    def since(self, value) -> 'SearchQueryBuilder':
        """SINCE <date>
         Messages whose internal date (disregarding time and timezone)
         is within or later than the specified date.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('SINCE {}'.format(get_date(value)))
        return self

    def smaller(self, value) -> 'SearchQueryBuilder':
        """SMALLER <n>
         Messages with an [RFC-2822] size smaller than the specified
         number of octets.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('SMALLER {}'.format(int(value)))
        return self

    def subject(self, value) -> 'SearchQueryBuilder':
        """SUBJECT <string>
         Messages that contain the specified string in the envelope
         structure's SUBJECT field.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('SUBJECT {}'.format(value))
        return self

    def text(self, value) -> 'SearchQueryBuilder':
        """TEXT <string>
         Messages that contain the specified string in the header or
         body of the message.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('TEXT {}'.format(value))
        return self

    def to(self, value) -> 'SearchQueryBuilder':
        """TO <string>
         Messages that contain the specified string in the envelope
         structure's TO field.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('TO {}'.format(value))
        return self

    def uid(self, value) -> 'SearchQueryBuilder':
        """UID <sequence set>
         Messages with unique identifiers corresponding to the specified
         unique identifier set.  Sequence set ranges are permitted.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('UID {}'.format(build_sequence(value)))
        return self

    def unanswered(self) -> 'SearchQueryBuilder':
        """UNANSWERED
         Messages that do not have the \Answered flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('UNANSWERED')
        return self

    def undeleted(self) -> 'SearchQueryBuilder':
        """UNDELETED
         Messages that do not have the \Deleted flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('UNDELETED')
        return self

    def undrfat(self) -> 'SearchQueryBuilder':
        """UNDRAFT
         Messages that do not have the \Draft flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('UNDRAFT')
        return self

    def unflagged(self) -> 'SearchQueryBuilder':
        """UNFLAGGED
         Messages that do not have the \Flagged flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('UNFLAGGED')
        return self

    def unkeyword(self, value) -> 'SearchQueryBuilder':
        """UNKEYWORD <flag>
         Messages that do not have the specified keyword flag set.
        :param value:
        :return: SearchQueryBuilder
        """
        self.__items.add('UNKEYWORD {}'.format(str(value)))
        return self

    def unseen(self) -> 'SearchQueryBuilder':
        """UNSEEN
         Messages that do not have the \Seen flag set.
        :return: SearchQueryBuilder
        """
        self.__items.add('UNSEEN')
        return self

    def build(self) -> Tuple[str, str]:
        """Builds string from provided data
        :return: tuple first sequence set, second query
        """
        if self.uids:
            self.uid(filter(None, (self.uids,)))
        seq_set = ''
        if self.sequence:
            seq_set = self._build_range()
        return seq_set, ' '.join(item for item in self.__items)

    def __repr__(self):
        return ' '.join(self.build())
