import pyvips
from pyvips import ffi, vips_lib, Error, _to_bytes

# import logging
# logger = logging.getLogger(__name__)


class Interpolate(pyvips.VipsObject):
    """Make interpolators for operators like :meth:`.affine`.

    """

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Interpolate, self).__init__(pointer)

    @staticmethod
    def new(name):
        """Make a new interpolator by name.

        Make a new interpolator from the libvips class nickname. For example::

            inter = pyvips.Interpolator.new('bicubic')

        You can get a list of all supported interpolators from the command-line
        with::

            $ vips -l interpolate

        See for example :meth:`.affine`.

        """

        # logger.debug('VipsInterpolate.new: name = %s', name)

        vi = vips_lib.vips_interpolate_new(_to_bytes(name))
        if vi == ffi.NULL:
            raise Error(f'no such interpolator {name}')

        return Interpolate(vi)


__all__ = ['Interpolate']
