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

is_PY3 = sys.version_info[0] == 3

if is_PY3:
    text_type = str
else:
    text_type = unicode

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
    void vips_shutdown (void);

    typedef struct _VipsImage VipsImage;
    typedef struct _GValue GValue;

    void* g_malloc (size_t size);
    void g_free (void* data);

    int vips_leak_set (int leak);

    char* vips_path_filename7 (const char* path);
    char* vips_path_mode7 (const char* path);

    GType vips_type_find (const char* basename, const char* nickname);
    const char* g_type_name (GType gtype);

''')

class Error(Exception):
    """An error from vips.

    message -- a high-level description of the error
    detail -- a string with some detailed diagnostics
    """
    def __init__(self, message, detail = None):
        self.message = message
        if detail is None or detail == "":
            detail = to_string(ffi.string(vips_lib.vips_error_buffer()))
            vips_lib.vips_error_clear()
        self.detail = detail

        logger.debug('Error %s %s', self.message, self.detail)

    def __str__(self):
        return '{0}\n  {1}'.format(self.message, self.detail)

argv = sys.argv[0]
if isinstance(argv, text_type):
    argv = argv.encode()

if vips_lib.vips_init(argv) != 0:
    raise Error('unable to init Vips')

def shutdown():
    logger.debug('Shutting down libvips')
    vips_lib.vips_shutdown()

logger.debug('Inited libvips')
logger.debug('')

def leak_set(leak):
    return vips_lib.vips_leak_set(leak)

def to_bytes(x):
    if isinstance(x, text_type):
        x = x.encode()
    return x

def to_string(x):
    if is_PY3 and isinstance(x, bytes):
        x = x.decode('utf-8')
    return x

def path_filename7(filename):
    return to_string(ffi.string(vips_lib.vips_path_filename7(to_bytes(filename))))

def path_mode7(filename):
    return to_string(ffi.string(vips_lib.vips_path_mode7(to_bytes(filename))))

def type_find(basename, nickname):
    return vips_lib.vips_type_find(to_bytes(basename), to_bytes(nickname))

def type_name(gtype):
    return to_string(ffi.string(gobject_lib.g_type_name(gtype)))

__all__ = ['ffi', 'vips_lib', 'gobject_lib', 'Error', 'leak_set',
           'to_bytes', 'to_string', 'type_find', 'type_name',
           'path_filename7', 'path_mode7', 'shutdown']
