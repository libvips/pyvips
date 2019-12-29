# flake8: noqa

import logging
import os
import sys
import atexit

logger = logging.getLogger(__name__)

# user code can override this null handler
logger.addHandler(logging.NullHandler())

# pull in our module version number, see also setup.py
from .version import __version__

# try to import our binary interface ... if that works, we are in API mode
API_mode = False
try:
    import _libvips

    logger.debug('Loaded binary module _libvips')

    ffi = _libvips.ffi
    vips_lib = _libvips.lib
    glib_lib = _libvips.lib
    gobject_lib = _libvips.lib

    # now check that the binary wrapper is for the same version of libvips that
    # we find ourseleves linking to at runtime ... if it isn't, we must fall 
    # back to ABI mode
    lib_major = vips_lib.vips_version(0)
    lib_minor = vips_lib.vips_version(1)
    wrap_major = vips_lib.VIPS_MAJOR_VERSION
    wrap_minor = vips_lib.VIPS_MINOR_VERSION
    logger.debug('Module generated for libvips %s.%s' % 
                 (wrap_major, wrap_minor)) 
    logger.debug('Linked to libvips %s.%s' % (lib_major, lib_minor)) 

    if wrap_major != lib_major or wrap_minor != lib_minor:
        raise Exception('bad wrapper version')

    API_mode = True

except Exception as e:
    logger.debug('Binary module load failed: %s' % e)
    logger.debug('Falling back to ABI mode')

    from cffi import FFI

    ffi = FFI()

    _is_windows = os.name == 'nt'
    _is_mac = sys.platform == 'darwin'

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
        _vips_libname = 'libvips.so.42'
        _gobject_libname = 'libgobject-2.0.so.0'

    # possibly use ctypes.util.find_library() to locate the lib?
    gobject_lib = ffi.dlopen(_gobject_libname)
    vips_lib = ffi.dlopen(_vips_libname)
    if _glib_libname:
        glib_lib = ffi.dlopen(_glib_libname)
    else:
        glib_lib = gobject_lib

    logger.debug('Loaded lib %s', vips_lib)
    logger.debug('Loaded lib %s', gobject_lib)

    ffi.cdef('''
        int vips_init (const char* argv0);
        int vips_version (int flag);
    ''')

if vips_lib.vips_init(sys.argv[0].encode()) != 0:
    raise Exception('unable to init libvips')

logger.debug('Inited libvips')

if not API_mode:
    from .vdecls import cdefs

    major = vips_lib.vips_version(0)
    minor = vips_lib.vips_version(1)
    micro = vips_lib.vips_version(2)
    features = {
        'major': major,
        'minor': minor,
        'micro': micro,
        'api': False,
    }

    ffi.cdef(cdefs(features))

from .error import *

# redirect all vips warnings to logging

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

if API_mode:
    @ffi.def_extern()
    def _log_handler_callback(domain, level, message, user_data):
        logger.log(GLogLevelFlags.LEVEL_TO_LOGGER[level],
                   '{0}: {1}'.format(_to_string(domain), _to_string(message)))

    # keep a ref to the cb to stop it being GCd
    _log_handler_cb = glib_lib._log_handler_callback
else:
    def _log_handler_callback(domain, level, message, user_data):
        logger.log(GLogLevelFlags.LEVEL_TO_LOGGER[level],
                   '{0}: {1}'.format(_to_string(domain), _to_string(message)))

    # keep a ref to the cb to stop it being GCd
    _log_handler_cb = ffi.callback('GLogFunc', _log_handler_callback)

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

from .enums import *
from .base import *
from .gobject import *
from .gvalue import *
from .vobject import *
from .vinterpolate import *
from .vconnection import *
from .vsource import *
from .vsourcecustom import *
from .vtarget import *
from .vtargetcustom import *
from .voperation import *
from .vimage import *
from .vregion import *

__all__ = [
    'Error', 'Image', 'Region', 'Introspect', 'Operation', 'GValue', 'Interpolate', 'GObject',
    'VipsObject', 'type_find', 'type_name', 'version', '__version__',
    'at_least_libvips', 'API_mode',
    'get_suffixes',
    'cache_set_max', 'cache_set_max_mem', 'cache_set_max_files',
]
