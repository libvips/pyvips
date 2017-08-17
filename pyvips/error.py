# errors from libvips

import sys
import logging

from pyvips import ffi, vips_lib

logger = logging.getLogger(__name__)

_is_PY3 = sys.version_info[0] == 3

if _is_PY3:
    text_type = str
else:
    text_type = unicode

ffi.cdef('''
    const char* vips_error_buffer (void);
    void vips_error_clear (void);

''')


def _to_bytes(x):
    """Convert to a byte string.

    Convert a Python unicode string to a utf-8-encoded byte string. You must
    call this on strings you pass to libvips.

    """

    if isinstance(x, text_type):
        x = x.encode()
    return x


def _to_string(x):
    """Convert to a unicode string.

    If x is a byte string, assume it is utf-8 and decode to a Python unicode
    string. You must call this on text strings you get back from libvips.

    """
    if _is_PY3 and isinstance(x, bytes):
        x = x.decode('utf-8')
    return x


class Error(Exception):
    """An error from vips.

    Attributes:
        message (str): a high-level description of the error
        detail (str): a string with some detailed diagnostics

    """

    def __init__(self, message, detail=None):
        self.message = message
        if detail is None or detail == "":
            detail = _to_string(ffi.string(vips_lib.vips_error_buffer()))
            vips_lib.vips_error_clear()
        self.detail = detail

        logger.debug('Error %s %s', self.message, self.detail)

    def __str__(self):
        return '{0}\n  {1}'.format(self.message, self.detail)


__all__ = [
    '_to_bytes', '_to_string', 'Error',
]
