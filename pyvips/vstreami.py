from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib, Error, _to_bytes

logger = logging.getLogger(__name__)


class Streami(pyvips.Stream):
    """An input stream.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Streami, self).__init__(pointer)

    @staticmethod
    def new_from_descriptor(descriptor):
        """Make a new stream from a file descriptor (a small integer).

        Make a new stream that is attached to the descriptor. For example::

            streami = pyvips.Streami.new_from_descriptor(0)

        Makes a descriptor attached to stdin.

        You can pass this stream to (for example) :meth:`new_from_stream`.

        """

        # logger.debug('VipsStreami.new_from_descriptor: descriptor = %d',
        #   descriptor)

        # streams are mutable, so we can't use the cache
        pointer = vips_lib.vips_streami_new_from_descriptor(descriptor)
        if pointer == ffi.NULL:
            raise Error("can't create input stream from descriptor {0}"
                        .format(descriptor))

        return Streami(pointer)

    @staticmethod
    def new_from_file(filename):
        """Make a new stream from a filename.

        Make a new stream that is attached to the named file. For example::

            streami = pyvips.Streami.new_from_file("myfile.jpg")

        You can pass this stream to (for example) :meth:`new_from_stream`.

        """

        # logger.debug('VipsStreami.new_from_file: filename = %s',
        #              filename)

        pointer = vips_lib.vips_streami_new_from_file(_to_bytes(filename))
        if pointer == ffi.NULL:
            raise Error("can't create input stream from filename {0}"
                        .format(filename))

        return Streami(pointer)

    @staticmethod
    def new_from_memory(data):
        """Make a new stream from a memory object.

        Make a new stream that is attached to the memory object. For example::

            streami = pyvips.Streami.new_from_memory("myfile.jpg")

        You can pass this stream to (for example) :meth:`new_from_stream`.

        The memory object can be anything that supports the Python buffer or
        memoryview protocol.

        """

        # logger.debug('VipsStreami.new_from_memory:')

        # py3:
        #   - memoryview has .nbytes for number of bytes in object
        #   - len() returns number of elements in top array
        # py2:
        #   - buffer has no nbytes member
        #   - but len() gives number of bytes in object
        start = ffi.from_buffer(data)
        nbytes = data.nbytes if hasattr(data, 'nbytes') else len(data)

        pointer = vips_lib.vips_streami_new_from_memory(start, nbytes)
        if pointer == ffi.NULL:
            raise Error("can't create input stream from memory")

        stream = Streami(pointer)

        # keep a secret reference to the input data to make sure it's not GCed
        stream._references = [data]

        return stream


__all__ = ['Streami']
