# -*- coding: utf-8 -*-

"""

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""

from cpython cimport bool

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
    #Returns TRUE if the string is valid IMAP-UTF-7 string. */
    bool imap_utf7_is_valid(const char *src)

cdef extern from "str.h":
    const char * str_c(string_t *)
    string_t *t_str_new(size_t)
    void str_free(string_t **)


def imap4_utf7_encode(data):
    """Encode a folder name using IMAP modified UTF-7 encoding.

    Input is unicode; output is bytes (Python 3) or str (Python 2). If
    non-unicode input is provided, the input is returned unchanged.
    """
    if not isinstance(data, str):
        return data
    cdef string_t *dest = t_str_new(255)
    try:
        if imap_utf8_to_utf7(data.encode(), dest) != 0:
            return data
        return str_c(dest)
    finally:
        str_free(&dest)

def imap4_utf7_decode(data):
    """Decode a folder name from IMAP modified UTF-7 encoding to unicode.

    Input is bytes (Python 3) or str (Python 2); output is always
    unicode. If non-bytes/str input is provided, the input is returned
    unchanged.
    """

    if not isinstance(data, bytes):
        return bytearray(data, 'utf-8')

    cdef string_t *dest = t_str_new(255)
    try:
        if imap_utf7_to_utf8(data, dest) != 0:
            return data
        return str_c(dest).decode('utf-8')
    finally:
        str_free(&dest)

