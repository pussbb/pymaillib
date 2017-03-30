# -*- coding: utf-8 -*-

"""

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

from libcpp cimport bool
from cpython.datetime cimport datetime_new
from libc.time cimport time_t, tm, mktime
from libc.stddef cimport size_t
from libc.string cimport strlen


cdef extern from "lib.h":
    pass

cdef extern from "buffer.h":
    cdef struct buffer:
        const void *data

cdef extern from "lib.h":
    ctypedef buffer string_t

cdef extern from "imap-utf7.h":
    # Convert an UTF-8 string to IMAP-UTF-7. Returns 0 if ok, -1 if src isn't
    # valid UTF-8.
    int imap_utf8_to_utf7(const char *src, string_t *dest)
    int t_imap_utf8_to_utf7(const char *src, const char **dest_r);
    # Convert IMAP-UTF-7 string to UTF-8. Returns 0 if ok, -1 if src isn't
    # valid IMAP-UTF-7.
    int imap_utf7_to_utf8(const char *src, string_t *dest)
    # Returns TRUE if the string is valid IMAP-UTF-7 string. */
    bool imap_utf7_is_valid(const char *src)

cdef extern from "str.h":
    const char * str_c(string_t *)
    string_t *t_str_new(size_t)
    void str_free(string_t **)

cdef extern from "iso8601-date.h":
    # Parses ISO8601 (RFC3339) date-time string. timezone_offset is filled with the
    # timezone's difference to UTC in minutes. Returned time_t timestamp is
    # compensated for time zone.
    bool iso8601_date_parse(const unsigned char *, size_t, time_t *, int *)
    # Equal to iso8601_date_parse, but writes uncompensated timestamp to tm_r. */
    bool iso8601_date_parse_tm(const unsigned char *, size_t, tm *, int *)

    # Create ISO8601 date-time string from given time struct in specified
    # timezone. A zone offset of zero will not to 'Z', but '+00:00'. If
    # zone_offset == INT_MAX, the time zone will be 'Z'. */
    const char *iso8601_date_create_tm(tm *, int )

    # Create ISO8601 date-time string from given time in local timezone. */
    const char *iso8601_date_create(time_t)



def imap4_utf7_encode(data):
    """Encode a folder name using IMAP modified UTF-7 encoding.

    """

    cdef string_t *dest = t_str_new(255)
    try:
        if imap_utf8_to_utf7(data.encode(), dest) != 0:
            return data
        return str_c(dest)
    finally:
        str_free(&dest)

def imap4_utf7_decode(bytes data):
    """Decode a folder name from IMAP modified UTF-7 encoding to unicode.

    """
    cdef string_t *dest = t_str_new(255)
    try:
        if imap_utf7_to_utf8(data, dest) != 0:
            return data
        return str_c(dest).decode('utf-8')
    finally:
        str_free(&dest)

from datetime import datetime, timezone, timedelta

def parse_date(value):
    """ in dovecot there are also message_date, imap_date files

    :param value:
    :return:
    """
    if isinstance(value, str):
        value =  value.encode()
    cdef tm tm4
    cdef int tz
    cdef bool result  = iso8601_date_parse_tm(<const unsigned char * >value, strlen(value), &tm4, &tz)
    if not result:
        raise Exception('Failed to parse {}'.format(value))

    return datetime.fromtimestamp(mktime(&tm4), timezone(timedelta(minutes=tz)))
