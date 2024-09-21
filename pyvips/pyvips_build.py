# flake8: noqa

import pkgconfig
from cffi import FFI

# we must have the vips package to be able to do anything
if not pkgconfig.exists('vips'):
    raise Exception('unable to find pkg-config package "vips"')
if pkgconfig.installed('vips', '< 8.2'):
    raise Exception('pkg-config "vips" is too old -- need libvips 8.2 or later')

major, minor, micro = [int(s) for s in pkgconfig.modversion('vips').split('.')]

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
    f"""
        #include <vips/vips.h>
        {compat}
    """,
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
