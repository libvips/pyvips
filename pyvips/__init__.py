import logging
import os
import sys

# flake8: noqa

from cffi import FFI

logger = logging.getLogger(__name__)

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

ffi.cdef('''
    int vips_init (const char* argv0);
''')

if vips_lib.vips_init(_to_bytes(sys.argv[0])) != 0:
    raise Error('unable to init libvips')

logger.debug('Inited libvips')
logger.debug('')

from .enums import *
from .base import *
from .gobject import GObject
from .gvalue import GValue
from .vobject import VipsObject
from .vinterpolate import Interpolate
from .voperation import Operation
from .vimage import Image

__all__ = [
    'Error', 'Image', 'Operation', 'GValue', 'Interpolate', 'GObject',
    'VipsObject', 'type_find', 'type_name'
]
