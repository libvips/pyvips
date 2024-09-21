import logging

import pyvips
from pyvips import ffi, vips_lib, Error, _to_bytes

logger = logging.getLogger(__name__)


class Target(pyvips.Connection):
    """An output connection.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Target, self).__init__(pointer)

    @staticmethod
    def new_to_descriptor(descriptor):
        """Make a new target to write to a file descriptor (a small
        integer).

        Make a new target that is attached to the descriptor. For example::

            target = pyvips.Target.new_to_descriptor(1)

        Makes a descriptor attached to stdout.

        You can pass this target to (for example) :meth:`write_to_target`.

        """

        # logger.debug('VipsTarget.new_to_descriptor: descriptor = %d',
        #   descriptor)

        # targets are mutable, so we can't use the cache
        pointer = vips_lib.vips_target_new_to_descriptor(descriptor)
        if pointer == ffi.NULL:
            raise Error(f"can't create output target from descriptor "
                        f'{descriptor}')

        return Target(pointer)

    @staticmethod
    def new_to_file(filename):
        """Make a new target to write to a file.

        Make a new target that will write to the named file. For example::

            target = pyvips.Target.new_to_file("myfile.jpg")

        You can pass this target to (for example) :meth:`write_to_target`.

        """

        # logger.debug('VipsTarget.new_to_file: filename = %s', filename)

        pointer = vips_lib.vips_target_new_to_file(_to_bytes(filename))
        if pointer == ffi.NULL:
            raise Error(f"can't create output target from filename {filename}")

        return Target(pointer)

    @staticmethod
    def new_to_memory():
        """Make a new target to write to an area of memory.

        Make a new target that will write to memory. For example::

            target = pyvips.Target.new_to_memory()

        You can pass this target to (for example) :meth:`write_to_target`.

        After writing to the target, fetch the bytes from the target object
        with `target.get("blob")`.

        """

        # logger.debug('VipsTarget.new_to_memory:')

        pointer = vips_lib.vips_target_new_to_memory()
        if pointer == ffi.NULL:
            raise Error("can't create output target from memory")

        return Target(pointer)


__all__ = ['Target']
