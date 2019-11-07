from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib, _to_string

logger = logging.getLogger(__name__)


class Stream(pyvips.VipsObject):
    """The abstract base Stream class.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Stream, self).__init__(pointer)

    def filename(self):
        """Get the filename assoiciated with a stream. Return None if there is
        no associated file.

        """

        so = ffi.cast('VipsStream *', self.pointer)
        pointer = vips_lib.vips_stream_filename(so)
        if pointer == ffi.NULL:
            return None
        else:
            return _to_string(pointer)

    def nick(self):
        """Make a human-readable name for a stream suitable for error
        messages.

        """

        so = ffi.cast('VipsStream *', self.pointer)
        pointer = vips_lib.vips_stream_nick(so)
        if pointer == ffi.NULL:
            return None
        else:
            return _to_string(pointer)


__all__ = ['Stream']
