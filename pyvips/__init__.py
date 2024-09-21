# flake8: noqa

import logging
import os
import sys
import atexit

logger = logging.getLogger(__name__)

# user code can override this null handler
logger.addHandler(logging.NullHandler())

def library_name(name, abi_number):
    is_windows = os.name == 'nt'
    is_mac = sys.platform == 'darwin'

    if is_windows:
        return f'lib{name}-{abi_number}.dll'
    elif is_mac:
        return f'lib{name}.{abi_number}.dylib'
    else:
        return f'lib{name}.so.{abi_number}'

# pull in our module version number
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
    logger.debug(f'Module generated for libvips {wrap_major}.{wrap_minor}')
    logger.debug(f'Linked to libvips {lib_major}.{lib_minor}')

    if wrap_major != lib_major or wrap_minor != lib_minor:
        raise Exception('bad wrapper version')

    API_mode = True

except Exception as e:
    logger.debug(f'Binary module load failed: {e}')
    logger.debug('Falling back to ABI mode')

    from cffi import FFI

    ffi = FFI()

    vips_lib = ffi.dlopen(library_name('vips', 42))
    glib_lib = vips_lib
    gobject_lib = vips_lib

    logger.debug('Loaded lib %s', vips_lib)

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

    # We can sometimes get dependent libraries from libvips -- either the platform
    # will open dependencies for us automatically, or the libvips binary has been
    # built to includes all main dependencies (common on windows, can happen
    # elsewhere).
    #
    # We must get glib functions from libvips if we can, since it will be the
    # one that libvips itself is using, and they will share runtime types.
    try:
        is_unified = gobject_lib.g_type_from_name(b'VipsImage') != 0
    except Exception:
        is_unified = False

    if not is_unified:
        glib_lib = ffi.dlopen(library_name('glib-2.0', 0))
        gobject_lib = ffi.dlopen(library_name('gobject-2.0', 0))

        logger.debug('Loaded lib %s', glib_lib)
        logger.debug('Loaded lib %s', gobject_lib)


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
        LEVEL_DEBUG: 10,
        LEVEL_INFO: 20,
        LEVEL_MESSAGE: 20,
        LEVEL_WARNING: 30,
        LEVEL_ERROR: 40,
        LEVEL_CRITICAL: 50,
    }


if API_mode:
    @ffi.def_extern()
    def _log_handler_callback(domain, level, message, user_data):
        logger.log(GLogLevelFlags.LEVEL_TO_LOGGER[level],
                   f'{_to_string(domain)}: {_to_string(message)}')

    # keep a ref to the cb to stop it being GCd
    _log_handler_cb = glib_lib._log_handler_callback
else:
    def _log_handler_callback(domain, level, message, user_data):
        logger.log(GLogLevelFlags.LEVEL_TO_LOGGER[level],
                   f'{_to_string(domain)}: {_to_string(message)}')

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
