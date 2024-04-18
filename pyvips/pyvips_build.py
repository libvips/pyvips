# flake8: noqa

import pkgconfig
from cffi import FFI

# we must have the vips package to be able to do anything
if not pkgconfig.exists('vips'):
    raise Exception('unable to find pkg-config package "vips"')
if pkgconfig.installed('vips', '< 8.2'):
    raise Exception('pkg-config "vips" is too old -- need libvips 8.2 or later')

# pkgconfig 1.5+ has modversion ... otherwise, use a small shim
try:
    from pkgconfig import modversion
except ImportError:
    def modversion(package):
        # will need updating once we hit 8.20 :(
        for i in range(20, 3, -1):
            if pkgconfig.installed(package, '>= 8.' + str(i)):
                # be careful micro version is always set to 0
                return '8.' + str(i) + '.0'
        return '8.2.0'

major, minor, micro = [int(s) for s in modversion('vips').split('.')]

ffibuilder = FFI()

# vips_value_set_blob_free and vips_area_free_cb compat for libvips < 8.6
compat = '''
int
vips_area_free_cb(void *mem, VipsArea *area)
{
    g_free(mem);

    return 0;
}

void
vips_value_set_blob_free(GValue* value, void* data, size_t length)
{
    vips_value_set_blob(value, (VipsCallbackFn) vips_area_free_cb,
        data, length);
}
''' if major == 8 and minor < 6 else ''

ffibuilder.set_source("_libvips",
    r"""
        #include <vips/vips.h>
    """ + compat,
    **pkgconfig.parse('vips'))

features = {
    'major': major,
    'minor': minor,
    'micro': micro,
    'api': True,
}


import vdecls

# handy for debugging
# with open('vips-source.txt','w') as f:
#     c = vdecls.cdefs(features)
#     f.write(c)

ffibuilder.cdef(vdecls.cdefs(features))

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
