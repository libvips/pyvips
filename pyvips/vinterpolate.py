# wrap VipsInterpolate

from __future__ import division

import logging

from pyvips import *

logger = logging.getLogger(__name__)

ffi.cdef('''
    typedef struct _VipsInterpolate {
        VipsObject parent_instance;

        // opaque
    } VipsInterpolate;

    VipsInterpolate* vips_interpolate_new (const char* name);

''')

class Interpolate(VipsObject):

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = {0}'.format(pointer))
        super(Interpolate, self).__init__(pointer)

    @staticmethod
    def new(name):
        # logger.debug('VipsInterpolate.new: name = {0}'.format(name))

        vi = vips_lib.vips_interpolate_new(name)
        if vi == ffi.NULL:
            raise Error('no such interpolator {0}'.format(name))

        return Interpolate(vi)
