import logging

import pyvips
from pyvips import ffi, vips_lib, Error, _to_bytes

logger = logging.getLogger(__name__)


class Source(pyvips.Connection):
    """An input connection.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Source, self).__init__(pointer)

    @staticmethod
    def new_from_descriptor(descriptor):
        """Make a new source from a file descriptor (a small integer).

        Make a new source that is attached to the descriptor. For example::

            source = pyvips.Source.new_from_descriptor(0)

        Makes a descriptor attached to stdin.

        You can pass this source to (for example) :meth:`new_from_source`.

        """

        # logger.debug('VipsSource.new_from_descriptor: descriptor = %d',
        #   descriptor)

        # sources are mutable, so we can't use the cache
        pointer = vips_lib.vips_source_new_from_descriptor(descriptor)
        if pointer == ffi.NULL:
            raise Error(f"can't create source from descriptor {descriptor}")

        return Source(pointer)

    @staticmethod
    def new_from_file(filename):
        """Make a new source from a filename.

        Make a new source that is attached to the named file. For example::

            source = pyvips.Source.new_from_file("myfile.jpg")

        You can pass this source to (for example) :meth:`new_from_source`.

        """

        # logger.debug('VipsSource.new_from_file: filename = %s',
        #              filename)

        pointer = vips_lib.vips_source_new_from_file(_to_bytes(filename))
        if pointer == ffi.NULL:
            raise Error(f"can't create source from filename {filename}")

        return Source(pointer)

    @staticmethod
    def new_from_memory(data):
        """Make a new source from a memory object.

        Make a new source that is attached to the memory object. For example::

            source = pyvips.Source.new_from_memory("myfile.jpg")

        You can pass this source to (for example) :meth:`new_from_source`.

        The memory object can be anything that supports the Python buffer or
        memoryview protocol.

        """

        # logger.debug('VipsSource.new_from_memory:')

        start = ffi.from_buffer(data)
        nbytes = data.nbytes if hasattr(data, 'nbytes') else len(data)

        pointer = vips_lib.vips_source_new_from_memory(start, nbytes)
        if pointer == ffi.NULL:
            raise Error("can't create input source from memory")

        source = Source(pointer)

        # keep a secret reference to the input data to make sure it's not GCed
        source._references = [data]

        return source


__all__ = ['Source']
