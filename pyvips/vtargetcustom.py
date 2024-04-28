import logging

import pyvips
from pyvips import ffi, vips_lib, at_least_libvips

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
            return handler(buf)

        self.signal_connect("write", interface_handler)

    def on_read(self, handler):
        """Attach a read handler.

        The interface is exactly as io.read(). The handler is given a number
        of bytes to fetch, and should return a bytes-like object containing up
        to that number of bytes. If there is no more data available, it should
        return None.

        Read handlers are optional for targets. If you do not set one, your
        target will be treated as unreadable and libvips will be unable to
        write some file types (just TIFF, as of the time of writing).

        """

        def interface_handler(buf):
            chunk = handler(len(buf))
            if chunk is None:
                return 0

            bytes_read = len(chunk)
            buf[:bytes_read] = chunk

            return bytes_read

        if at_least_libvips(8, 13):
            self.signal_connect("read", interface_handler)

    def on_seek(self, handler):
        """Attach a seek handler.

        The interface is the same as io.seek(), so the handler is passed
        parameters for offset and whence with the same meanings.

        However, the handler MUST return the new seek position. A simple way
        to do this is to call io.tell() and return that result.

        Seek handlers are optional. If you do not set one, your target will be
        treated as unseekable and libvips will be unable to write some file
        types (just TIFF, as of the time of writing).

        """

        if at_least_libvips(8, 13):
            self.signal_connect("seek", handler)

    def on_end(self, handler):
        """Attach an end handler.

        This optional handler is called at the end of write. It should do any
        cleaning up necessary, and return 0 on success and -1 on error.

        """

        if not at_least_libvips(8, 13):
            # fall back for older libvips
            self.on_finish(handler)
        else:
            self.signal_connect("end", handler)

    def on_finish(self, handler):
        """Attach a finish handler.

        For libvips 8.13 and later, this method is deprecated in favour of
        :meth:`on_end`.

        """

        self.signal_connect("finish", handler)


__all__ = ['TargetCustom']
