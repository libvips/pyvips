# basic defs and link to ffi

import logging

from pyvips import ffi, glib_lib, vips_lib, gobject_lib, _to_string, _to_bytes

ffi.cdef('''
    typedef struct _VipsImage VipsImage;
    typedef struct _GValue GValue;

    void* g_malloc (size_t size);
    void g_free (void* data);

    int vips_leak_set (int leak);

    char* vips_path_filename7 (const char* path);
    char* vips_path_mode7 (const char* path);

    GType vips_type_find (const char* basename, const char* nickname);
    const char* vips_nickname_find (GType type);

    const char* g_type_name (GType gtype);
    GType g_type_from_name (const char* name);

    typedef void* (*VipsTypeMap2Fn) (GType type);
    void* vips_type_map (GType base, VipsTypeMap2Fn fn);

    typedef void (*GLogFunc) (const char* log_domain,
        int log_level,
        const char* message, void* user_data);
    int g_log_set_handler (const char* log_domain,
        int log_levels,
        GLogFunc log_func, void* user_data);

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


logger = logging.getLogger(__name__)


def _log_handler(domain, level, message, user_data):
    print "_log_handler: seen message", message
    if level == GLogLevelFlags.LEVEL_WARNING: 
        logger.warning('{0}: {1]'.format(domain, message))


# redirect all vips warnings to logging
glib_lib.g_log_set_handler('VIPS', 
                           GLogLevelFlags.LEVEL_WARNING | 
                           GLogLevelFlags.FLAG_FATAL | 
                           GLogLevelFlags.FLAG_RECURSION,
                           ffi.callback('GLogFunc', _log_handler), ffi.NULL)


def leak_set(leak):
    """Enable or disable libvips leak checking.

    With this enabled, libvips will check for object and area leaks on exit.
    Enabling this option will make libvips run slightly more slowly.
    """
    return vips_lib.vips_leak_set(leak)


def path_filename7(filename):
    return _to_string(ffi.string(vips_lib.vips_path_filename7(
        _to_bytes(filename))))


def path_mode7(filename):
    return _to_string(ffi.string(vips_lib.vips_path_mode7(
        _to_bytes(filename))))


def type_find(basename, nickname):
    """Get the GType for a name.

    Looks up the GType for a nickname. Types below basename in the type
    hierarchy are searched.
    """
    return vips_lib.vips_type_find(_to_bytes(basename), _to_bytes(nickname))


def type_name(gtype):
    """Return the name for a GType."""

    return _to_string(ffi.string(gobject_lib.g_type_name(gtype)))


def nickname_find(gtype):
    """Return the nickname for a GType."""

    return _to_string(ffi.string(vips_lib.vips_nickname_find(gtype)))


def type_from_name(name):
    """Return the GType for a name."""

    return gobject_lib.g_type_from_name(_to_bytes(name))


def type_map(gtype, fn):
    """Map fn over all child types of gtype."""
    cb = ffi.callback('VipsTypeMap2Fn', fn)
    return vips_lib.vips_type_map(gtype, cb)


__all__ = [
    'leak_set',
    'path_filename7',
    'path_mode7',
    'type_find',
    'nickname_find',
    'type_name',
    'type_map',
    'type_from_name',
]
