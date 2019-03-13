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
# will need updating once we hit 8.20 :(
major = 8
minor = 2
micro = 0
for i in range(20, 3, -1):
    if pkgconfig.installed('vips', '>= 8.' + str(i)):
        minor = i
        break

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
