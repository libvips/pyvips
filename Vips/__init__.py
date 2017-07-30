# wrapper for libvips

import sys
from cffi import FFI

def log(msg):
    print msg

ffi = FFI()

# possibly use ctypes.util.find_library() to locate the lib
# need a different name on windows? or os x?
# on win, may need to explcitly load other libraries as well
vips_lib = ffi.dlopen('libvips.so')
gobject_lib = ffi.dlopen('libgobject-2.0.so')

log('Loaded lib {0}'.format(vips_lib))
log('Loaded lib {0}'.format(gobject_lib))

# apparently the best way to find out
is_64bits = sys.maxsize > 2 ** 32

is_PY2 = sys.version_info.major == 2

ffi.cdef('''
    const char* vips_error_buffer (void);
    void vips_error_clear (void);

    int vips_init (const char* argv0);

    typedef struct _VipsImage VipsImage;

    void* g_malloc(size_t size);
    void g_free(void* data);


''')

def error(msg):
    print(msg)
    sys.exit(-1)

def vips_get_error():
    errstr = ffi.string(vips_lib.vips_error_buffer())
    vips_lib.vips_error_clear()

    return errstr

def vips_error():
    error(vips_get_error())

if vips_lib.vips_init('') != 0:
    vips_error()

log('Inited libvips')
log('')

# a callback that triggers g_free()
@ffi.callback('void(void*)')
def g_free_callback(ptr):
    gobject_lib.g_free(ptr)

from gvalue import GValue
from gobject import GObject
from vobject import VipsObject
