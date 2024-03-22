import logging

import pyvips
from pyvips import ffi, vips_lib, _to_string

logger = logging.getLogger(__name__)


class Connection(pyvips.VipsObject):
    """The abstract base Connection class.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Connection, self).__init__(pointer)

    def filename(self):
        """Get the filename associated with a connection. Return None if there
        is no associated file.

        """

        so = ffi.cast('VipsConnection *', self.pointer)
        pointer = vips_lib.vips_connection_filename(so)
        if pointer == ffi.NULL:
            return None
        else:
            return _to_string(pointer)

    def nick(self):
        """Make a human-readable name for a connection suitable for error
        messages.

        """

        so = ffi.cast('VipsConnection *', self.pointer)
        pointer = vips_lib.vips_connection_nick(so)
        if pointer == ffi.NULL:
            return None
        else:
            return _to_string(pointer)


__all__ = ['Connection']
