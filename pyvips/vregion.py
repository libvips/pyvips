# wrap VipsRegion

from __future__ import division

import pyvips
from pyvips import ffi, glib_lib, vips_lib, Error, at_least_libvips


class Region(pyvips.VipsObject):
    """Wrap a VipsRegion object.

    """

    def __init__(self, pointer):
        # logger.debug('Image.__init__: pointer = %s', pointer)
        super(Region, self).__init__(pointer)

    # constructors

    @staticmethod
    def new(image):
        """Make a region on an image.

        Returns:
            A new :class:`.Region`.

        Raises:
            :class:`.Error`

        """

        pointer = vips_lib.vips_region_new(image.pointer)
        if pointer == ffi.NULL:
            raise Error('unable to make region')

        return pyvips.Region(pointer)

    def width(self):
        """Width of pixels held by region."""
        if not at_least_libvips(8, 8):
            raise Error('libvips too old')

        return vips_lib.vips_region_width(self.pointer)

    def height(self):
        """Height of pixels held by region."""
        if not at_least_libvips(8, 8):
            raise Error('libvips too old')

        return vips_lib.vips_region_height(self.pointer)

    def fetch(self, x, y, w, h):
        """Fill a region with pixel data.

        Pixels are filled with data!

        Returns:
            Pixel data.

        Raises:
            :class:`.Error`

        """

        if not at_least_libvips(8, 8):
            raise Error('libvips too old')

        psize = ffi.new('size_t *')
        pointer = vips_lib.vips_region_fetch(self.pointer, x, y, w, h, psize)
        if pointer == ffi.NULL:
            raise Error('unable to fetch from region')

        pointer = ffi.gc(pointer, glib_lib.g_free)
        return ffi.buffer(pointer, psize[0])


__all__ = ['Region']
