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
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Streamou, self).__init__(pointer)

    @staticmethod
    def new(descriptor):
        """Make a new streamou.

        Attach handlers to the `"write"` and `"finish"` signals to implement
        other behavours. Subclass this to add state.

        You can pass this stream to (for example) :meth:`write_to_stream`.

        """

        # logger.debug('VipsStreamo.new_to_descriptor: descriptor = %d',
        #   descriptor)

        # streams are mutable, so we can't use the cache
        pointer = vips_lib.vips_streamou_new()
        if pointer == ffi.NULL:
            raise Error("can't create streamou")

        return Streamou(pointer)


__all__ = ['Streamou']
