# flake8: noqa

import logging
import os
import sys
import atexit

from cffi import FFI

# pull in our module version number, see also setup.py
from .version import __version__

logger = logging.getLogger(__name__)

# user code can override this null handler
logger.addHandler(logging.NullHandler())

ffi = FFI()

_is_windows = os.name == 'nt'
_is_mac = sys.platform == 'darwin'
_is_64bits = sys.maxsize > 2 ** 32

# yuk
if _is_windows:
    _glib_libname = 'libglib-2.0-0.dll'
    _gobject_libname = 'libgobject-2.0-0.dll'
    _vips_libname = 'libvips-42.dll'
elif _is_mac:
    _glib_libname = None
    _vips_libname = 'libvips.42.dylib'
    _gobject_libname = 'libgobject-2.0.dylib'
else:
    _glib_libname = None
    _vips_libname = 'libvips.so'
    _gobject_libname = 'libgobject-2.0.so'

# possibly use ctypes.util.find_library() to locate the lib?
gobject_lib = ffi.dlopen(_gobject_libname)
vips_lib = ffi.dlopen(_vips_libname)
if _glib_libname:
    glib_lib = ffi.dlopen(_glib_libname)
else:
    glib_lib = gobject_lib

logger.debug('Loaded lib %s', vips_lib)
logger.debug('Loaded lib %s', gobject_lib)

# GType is an int the size of a pointer ... I don't think we can just use
# size_t, sadly
if _is_64bits:
    ffi.cdef('''
        typedef uint64_t GType;
    ''')
else:
    ffi.cdef('''
        typedef uint32_t GType;
    ''')

from .error import *

# redirect all vips warnings to logging

ffi.cdef('''
    typedef void (*GLogFunc) (const char* log_domain,
        int log_level,
        const char* message, void* user_data);
    int g_log_set_handler (const char* log_domain,
        int log_levels,
        GLogFunc log_func, void* user_data);

    void g_log_remove_handler (const char* log_domain, int handler_id);

''')

class GLogLevelFlags(object):
    # log flags 
    FLAG_RECURSION          = 1 << 0
    FLAG_FATAL              = 1 << 1

    # GLib log levels 
    LEVEL_ERROR             = 1 << 2       # always fatal 
    LEVEL_CRITICAL          = 1 << 3
    LEVEL_WARNING           = 1 << 4
    LEVEL_MESSAGE           = 1 << 5
    LEVEL_INFO              = 1 << 6
    LEVEL_DEBUG             = 1 << 7

    LEVEL_TO_LOGGER = {
        LEVEL_DEBUG : 10,
        LEVEL_INFO : 20,
        LEVEL_MESSAGE : 20,
        LEVEL_WARNING : 30,
        LEVEL_ERROR : 40,
        LEVEL_CRITICAL : 50,
    }

def _log_handler(domain, level, message, user_data):
    logger.log(GLogLevelFlags.LEVEL_TO_LOGGER[level], 
               '{0}: {1}'.format(_to_string(ffi.string(domain)), 
                                 _to_string(ffi.string(message))))

# keep a ref to the cb to stop it being GCd
_log_handler_cb = ffi.callback('GLogFunc', _log_handler)
_log_handler_id = glib_lib.g_log_set_handler(_to_bytes('VIPS'), 
                           GLogLevelFlags.LEVEL_DEBUG | 
                           GLogLevelFlags.LEVEL_INFO | 
                           GLogLevelFlags.LEVEL_MESSAGE | 
                           GLogLevelFlags.LEVEL_WARNING | 
                           GLogLevelFlags.LEVEL_CRITICAL | 
                           GLogLevelFlags.LEVEL_ERROR | 
                           GLogLevelFlags.FLAG_FATAL | 
                           GLogLevelFlags.FLAG_RECURSION,
                           _log_handler_cb, ffi.NULL)

# ffi doesn't like us looking up methods during shutdown: make a note of the
# remove handler here
_remove_handler = glib_lib.g_log_remove_handler

# we must remove the handler on exit or libvips may try to run the callback
# during shutdown
def _remove_log_handler():
    global _log_handler_id
    global _remove_handler

    if _log_handler_id:
        _remove_handler(_to_bytes('VIPS'), _log_handler_id)
        _log_handler_id = None

atexit.register(_remove_log_handler)

ffi.cdef('''
    int vips_init (const char* argv0);
''')

if vips_lib.vips_init(_to_bytes(sys.argv[0])) != 0:
    raise Error('unable to init libvips')

logger.debug('Inited libvips')
logger.debug('')

from .enums import *
from .base import *
from .gobject import *
from .gvalue import *
from .vobject import *
from .vinterpolate import *
from .voperation import *
from .vimage import *

__all__ = [
    'Error', 'Image', 'Operation', 'GValue', 'Interpolate', 'GObject',
    'VipsObject', 'type_find', 'type_name', 'version', '__version__',
    'at_least_libvips',
    'cache_set_max', 'cache_set_max_mem', 'cache_set_max_files'
]
