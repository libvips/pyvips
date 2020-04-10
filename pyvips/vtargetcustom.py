from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib

logger = logging.getLogger(__name__)


class TargetCustom(pyvips.Target):
    """An output target you can connect action signals to to implement
    behaviour.

    """

    def __init__(self):
        """Make a new target you can customise.

        You can pass this target to (for example) :meth:`write_to_target`.

        """

        target = ffi.cast('VipsTarget*', vips_lib.vips_target_custom_new())
        super(TargetCustom, self).__init__(target)

    def on_write(self, handler):
        """Attach a write handler.

        The interface is exactly as io.write(). The handler is given a
        bytes-like object to write, and should return the number of bytes
        written.

        """

        def interface_handler(buf):
            bytes_written = handler(buf)
            # py2 will often return None for bytes_written ... replace with
            # the length of the string
            if bytes_written is None:
                bytes_written = len(buf)

            return bytes_written

        self.signal_connect("write", interface_handler)

    def on_finish(self, handler):
        """Attach a finish handler.

        This optional handler is called at the end of write. It should do any
        cleaning up necessary.

        """

        self.signal_connect("finish", handler)


__all__ = ['TargetCustom']
