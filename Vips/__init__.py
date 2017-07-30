# wrapper for libvips

import sys
from cffi import FFI

ffi = FFI()

# possibly use ctypes.util.find_library() to locate the lib
# need a different name on windows? or os x?
# on win, may need to explcitly load other libraries as well
vips = ffi.dlopen('libvips.so')
gobject = ffi.dlopen('libgobject-2.0.so')

print('Loaded lib {0}'.format(vips))
print('Loaded lib {0}'.format(gobject))

# apparently the best way to find out
is_64bits = sys.maxsize > 2 ** 32

is_PY2 = sys.version_info.major == 2

ffi.cdef('''
    const char* vips_error_buffer (void);
    void vips_error_clear (void);

    int vips_init (const char* argv0);

    void vips_object_print_all (void);

    typedef struct _VipsImage VipsImage;

    void* g_malloc(size_t size);
    void g_free(void* data);

    void g_object_ref (void* object);
    void g_object_unref (void* object);

''')

def error(msg):
    print(msg)
    sys.exit(-1)

def vips_get_error():
    errstr = ffi.string(vips.vips_error_buffer())
    vips.vips_error_clear()

    return errstr

def vips_error():
    error(vips_get_error())

if vips.vips_init('') != 0:
    vips_error()

print 'Inited libvips'
print ''

def log(msg):
    print msg

def print_all(msg):
    gc.collect()
    print(msg)
    vips.vips_object_print_all()
    print()

# a callback that triggers g_free()
@ffi.callback('void(void*)')
def g_free_callback(ptr):
    glib.g_free(ptr)

from gvalue import GValue
