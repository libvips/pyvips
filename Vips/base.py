# basic defs and link to ffi

from __future__ import division

import logging
import sys
from cffi import FFI

logger = logging.getLogger(__name__)

ffi = FFI()

# possibly use ctypes.util.find_library() to locate the lib
# need a different name on windows? or os x?
# on win, may need to explcitly load other libraries as well
vips_lib = ffi.dlopen('libvips.so')
gobject_lib = ffi.dlopen('libgobject-2.0.so')

logger.debug('Loaded lib {0}'.format(vips_lib))
logger.debug('Loaded lib {0}'.format(gobject_lib))

# apparently the best way to find out
is_64bits = sys.maxsize > 2 ** 32

# GType is an int the size of a pointer ... I don't think we can just use
# size_t, sadly
if is_64bits:
    ffi.cdef('''
        typedef uint64_t GType;
    ''')
else:
    ffi.cdef('''
        typedef uint32_t GType;
    ''')

ffi.cdef('''
    const char* vips_error_buffer (void);
    void vips_error_clear (void);

    int vips_init (const char* argv0);

    typedef struct _VipsImage VipsImage;
    typedef struct _GValue GValue;

    void* g_malloc(size_t size);
    void g_free(void* data);

''')

class Error(Exception):
    """An error from vips.

    message -- a high-level description of the error
    detail -- a string with some detailed diagnostics
    """
    def __init__(self, message, detail = None):
        self.message = message
        if detail == None or detail == "":
            detail = ffi.string(vips_lib.vips_error_buffer())
            vips_lib.vips_error_clear()
        self.detail = detail

        logger.debug('Error %s %s', self.message, self.detail)

    def __str__(self):
        return '{0}\n  {1}'.format(self.message, self.detail)

if vips_lib.vips_init(sys.argv[0]) != 0:
    raise Error('unable to init Vips')

logger.debug('Inited libvips')
logger.debug('')

# a callback that triggers g_free()
@ffi.callback('void(void*)')
def g_free_callback(ptr):
    gobject_lib.g_free(ptr)

__all__ = ['ffi', 'g_free_callback', 'vips_lib', 'gobject_lib', 'Error']
