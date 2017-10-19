import pkgconfig

# we must have the vips package to be able to do anything
if not pkgconfig.exists('vips'): 
    raise Exception('unable to find pkg-config package "vips"')
if pkgconfig.installed('vips', '< 8.2'):
    raise Exception('pkg-config "vips" is too old -- need libvips 8.2 or later')

from cffi import FFI

ffibuilder = FFI()

# this is very hacky ... cffi in API mode won't let us cast function pointers,
# so we can't pass vips_free() as a vipsCallbackFn, which we need to be able to
# do when we set a blob
# 
# to fix this, we rename vips_free during the vips header load as
# real_vips_free, then declare a fake type ourselves that decl.py then hooks up
# to

ffibuilder.set_source("_libvips",
    r""" 
        #define vips_free real_vips_free
        #include <vips/vips.h>
        #undef vips_free

        extern VipsCallbackFn vips_free;
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

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
