from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib, Error, _to_bytes, _to_string

logger = logging.getLogger(__name__)


class Streamo(pyvips.Stream):
    """An output stream.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Streamo, self).__init__(pointer)

    @staticmethod
    def new_to_descriptor(descriptor):
        """Make a new output stream to write to a file descriptor (a small 
        integer).

        Make a new stream that is attached to the descriptor. For example::

            streamo = pyvips.Streamo.new_to_descriptor(1)

        Makes a descriptor attached to stdout.

        You can pass this stream to (for example) :meth:`write_to_stream`.

        """

        # logger.debug('VipsStreamo.new_to_descriptor: descriptor = %d', 
        #   descriptor)

        # streams are mutable, so we can't use the cache 
        pointer = vips_lib.vips_streamo_new_to_descriptor(descriptor)
        if pointer == ffi.NULL:
            raise Error("can't create output stream from descriptor {0}"
                        .format(descriptor))

        return Streamo(pointer)

    @staticmethod
    def new_to_filename(filename):
        """Make a new stream to write to a filename.

        Make a new stream that will write to the named file. For example::

            streamo = pyvips.Streamo.new_to_filename("myfile.jpg")

        You can pass this stream to (for example) :meth:`write_to_stream`.

        """

        # logger.debug('VipsStreamo.new_to_filename: filename = %s', filename)

        pointer = vips_lib.vips_streamo_new_to_filename(_to_bytes(filename))
        if pointer == ffi.NULL:
            raise Error("can't create output stream from filename {0}"
                        .format(filename))

        return Streamo(pointer)

    @staticmethod
    def new_to_memory():
        """Make a new stream to write to an area of memory.

        Make a new stream that will write to memory. For example::

            streamo = pyvips.Streamo.new_to_memory()

        You can pass this stream to (for example) :meth:`write_to_stream`.

        After writing to the stream, fetch the bytes from the stream object
        with `streamo.get("blob")`.

        """

        # logger.debug('VipsStreamo.new_to_memory:')

        pointer = vips_lib.vips_streamo_new_to_memory()
        if pointer == ffi.NULL:
            raise Error("can't create output stream from memory")

        return Streamo(pointer)


__all__ = ['Streamo']
