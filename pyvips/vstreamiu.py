from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib, Error

logger = logging.getLogger(__name__)


class Streamiu(pyvips.Streami):
    """An input stream you can connect action signals to to implement
    behaviour.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Streamiu, self).__init__(pointer)

    @staticmethod
    def new():
        """Make a new streamiu.

        Attach handlers to the `"read"` and `"seek"` signals to implement
        other behavours. Subclass this to add state.

        You can pass this stream to (for example) :meth:`new_from_stream`.

        """

        # logger.debug('VipsStreamiu.new:

        # streams are mutable, so we can't use the cache
        pointer = vips_lib.vips_streamiu_new()
        if pointer == ffi.NULL:
            raise Error("can't create streamiu")

        return Streamiu(pointer)


__all__ = ['Streamiu']
