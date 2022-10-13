# errors from libvips

import sys
import logging

from pyvips import ffi, vips_lib, glib_lib

logger = logging.getLogger(__name__)

_is_PY3 = sys.version_info[0] == 3

if _is_PY3:
    # pathlib is not part of Python 2 stdlib
    from pathlib import Path
    text_type = str, Path
    byte_type = bytes
else:
    text_type = unicode  # noqa: F821
    byte_type = str


def _to_bytes(x):
    """Convert to a byte string.

    Convert a Python unicode string or a pathlib.Path to a utf-8-encoded
    byte string. You must call this on strings you pass to libvips.

    """
    if isinstance(x, text_type):
        # n.b. str also converts pathlib.Path objects
        x = str(x).encode('utf-8')

    return x


def _to_string(x):
    """Convert to a unicode string.

    If x is a byte string, assume it is utf-8 and decode to a Python unicode
    string. You must call this on text strings you get back from libvips.

    """
    if x == ffi.NULL:
        x = 'NULL'
    else:
        x = ffi.string(x)
        if isinstance(x, byte_type):
            x = x.decode('utf-8')

    return x


def _to_string_copy(x):
    """Convert to a unicode string, and auto-free.

    As _to_string(), but also tag x as a pointer to a memory area that must
    be freed with g_free().

    """
    return _to_string(ffi.gc(x, glib_lib.g_free))


class Error(Exception):
    """An error from vips.

    Attributes:
        message (str): a high-level description of the error
        detail (str): a string with some detailed diagnostics

    """

    def __init__(self, message, detail=None):
        self.message = message
        if detail is None or detail == "":
            detail = _to_string(vips_lib.vips_error_buffer())
            vips_lib.vips_error_clear()
        self.detail = detail

        logger.debug('Error %s %s', self.message, self.detail)

    def __str__(self):
        return '{0}\n  {1}'.format(self.message, self.detail)


__all__ = [
    '_to_bytes', '_to_string', '_to_string_copy', 'Error',
]
