from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib, Error

logger = logging.getLogger(__name__)


class Streamou(pyvips.Streamo):
    """An output stream you can connect action signals to to implement
    behaviour.

    """

    def __init__(self, pointer):
        super(Streamou, self).__init__(pointer)

    @staticmethod
    def new():
        """Make a new stream from a file descriptor (a small integer).

        Attach handlers to the `"write"` and `"finish"` signals to implement
        other behavours. Subclass this to add state.

        You can pass this stream to (for example) :meth:`write_to_stream`.

        """

        # logger.debug('VipsStreamou.new:')
        pointer = vips_lib.vips_streamou_new()
        if pointer == ffi.NULL:
            raise Error("can't create streamou")

        return Streamou(pointer)


__all__ = ['Streamou']
