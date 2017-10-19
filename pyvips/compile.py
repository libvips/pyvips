# flake8: noqa

import pkgconfig

# we must have the vips package to be able to do anything
if not pkgconfig.exists('vips'): 
    raise Exception('unable to find pkg-config package "vips"')
if pkgconfig.installed('vips', '< 8.2'):
    raise Exception('pkg-config "vips" is too old -- need libvips 8.2 or later')

from cffi import FFI

ffibuilder = FFI()

ffibuilder.set_source("_libvips",
    r""" 
        #include <vips/vips.h>
    """, 
    **pkgconfig.parse('vips'))

features = {
    # in API mode
    'api': True,
    # at_least_libvips(8, 6):
    'blend_mode': pkgconfig.installed('vips', '>= 8.6')
}

import decls

ffibuilder.cdef(decls.cdefs(features))

ffibuilder.compile()
