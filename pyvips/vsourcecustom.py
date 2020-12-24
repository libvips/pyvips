from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib

logger = logging.getLogger(__name__)


class SourceCustom(pyvips.Source):
    """Custom sources allow reading data from otherwise unsupported sources.
    Requires libvips `>= 8.9.0`.

    To use, create a SourceCustom object, then provide callbacks to
    :meth:`on_read` and :meth:`on_seek`.
    """

    def __init__(self):
        """Make a new custom source.

        You can pass this source to (for example) :meth:`new_from_source`.

        """

        source = ffi.cast('VipsSource*', vips_lib.vips_source_custom_new())
        super(SourceCustom, self).__init__(source)

    def on_read(self, handler):
        """Attach a read handler.

        The interface is exactly as io.read(). The handler is given a number
        of bytes to fetch, and should return a bytes-like object containing up
        to that number of bytes. If there is no more data available, it should
        return None.

        """

        def interface_handler(buf):
            chunk = handler(len(buf))
            if chunk is None:
                return 0

            bytes_read = len(chunk)
            buf[:bytes_read] = chunk

            return bytes_read

        self.signal_connect("read", interface_handler)

    def on_seek(self, handler):
        """Attach a seek handler.

        The interface is the same as io.seek(), so the handler is passed
        parameters for offset and whence with the same meanings.

        However, the handler MUST return the new seek position. A simple way
        to do this is to call io.tell() and return that result.

        Seek handlers are optional. If you do not set one, your source will be
        treated as unseekable and libvips will do extra caching.

        """

        self.signal_connect("seek", handler)


__all__ = ['SourceCustom']
