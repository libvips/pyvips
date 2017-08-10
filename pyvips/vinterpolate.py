"""
:mod:`vinterpolate` -- An interpolator
======================================

.. module:: vinterpolate
    :synopsis: Interpolate values between points in various ways. 
.. moduleauthor:: John Cupitt <jcupitt@gmail.com>
.. moduleauthor:: Kleis Auke Wolthuizen <x@y.z>

Interpolators!

"""

from __future__ import division

import logging

import pyvips
from pyvips import ffi, vips_lib, Error, to_bytes

logger = logging.getLogger(__name__)

ffi.cdef('''
    typedef struct _VipsInterpolate {
        VipsObject parent_instance;

        // opaque
    } VipsInterpolate;

    VipsInterpolate* vips_interpolate_new (const char* name);

''')


class Interpolate(pyvips.VipsObject):
    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Interpolate, self).__init__(pointer)

    @staticmethod
    def new(name):
        # logger.debug('VipsInterpolate.new: name = %s', name)

        vi = vips_lib.vips_interpolate_new(to_bytes(name))
        if vi == ffi.NULL:
            raise Error('no such interpolator {0}'.format(name))

        return Interpolate(vi)
