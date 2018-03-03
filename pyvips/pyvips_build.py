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

# this is awful, why doesn't pkgconfig let us get the modversion?
major = 8
minor = 2
micro = 0
if pkgconfig.installed('vips', '>= 8.6'):
    minor = 6
elif pkgconfig.installed('vips', '>= 8.5'):
    minor = 5
elif pkgconfig.installed('vips', '>= 8.4'):
    minor = 4

features = {
    'major': major,
    'minor': minor,
    'micro': micro,
    'api': True,
}

from pyvips import decls

# handy for debugging
#with open('vips-source.txt','w') as f:
#    c = decls.cdefs(features)
#    f.write(c)

ffibuilder.cdef(decls.cdefs(features))

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
