from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib, Error

logger = logging.getLogger(__name__)


class Streamou(pyvips.Streamo):
    """An output stream you can connect action signals to to implement
    behaviour.

    Attach handlers to the `"write"` and `"finish"` signals to implement
    other behavours. Subclass this to add state.

    You can pass this stream to (for example) :meth:`write_to_stream`.

    """

    def __init__(self):
        pointer = vips_lib.vips_streamou_new()
        if pointer == ffi.NULL:
            raise Error("can't create streamou")

        super(Streamou, self).__init__(pointer)


__all__ = ['Streamou']
