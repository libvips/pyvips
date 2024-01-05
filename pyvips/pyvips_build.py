# flake8: noqa

import pkgconfig
from cffi import FFI

# we must have the vips package to be able to do anything
if not pkgconfig.exists('vips'): 
    raise Exception('unable to find pkg-config package "vips"')
if pkgconfig.installed('vips', '< 8.2'):
    raise Exception('pkg-config "vips" is too old -- need libvips 8.2 or later')

ffibuilder = FFI()

ffibuilder.set_source("_libvips",
    r""" 
        #include <vips/vips.h>
    """, 
    **pkgconfig.parse('vips'))

major, minor, micro = [int(s) for s in pkgconfig.modversion('vips').split('.')]

features = {
    'major': major,
    'minor': minor,
    'micro': micro,
    'api': True,
}

import vdecls

# handy for debugging
#with open('vips-source.txt','w') as f:
#    c = vdecls.cdefs(features)
#    f.write(c)

ffibuilder.cdef(vdecls.cdefs(features))

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
