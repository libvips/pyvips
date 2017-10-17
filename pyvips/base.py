# basic defs and link to ffi


from pyvips import ffi, vips_lib, gobject_lib, _to_string, _to_bytes, Error


def leak_set(leak):
    """Enable or disable libvips leak checking.

    With this enabled, libvips will check for object and area leaks on exit.
    Enabling this option will make libvips run slightly more slowly.
    """
    return vips_lib.vips_leak_set(leak)


def version(flag):
    """Get the major, minor or micro version number of the libvips library.

    Args:
        flag (int): Pass flag 0 to get the major version number, flag 1 to
            get minor, flag 2 to get micro.

    Returns:
        The version number,

    Raises:
        :class:`.Error`

    """

    value = vips_lib.vips_version(flag)
    if value < 0:
        raise Error('unable to get library version')

    return value


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
    'version',
    'path_filename7',
    'path_mode7',
    'type_find',
    'nickname_find',
    'type_name',
    'type_map',
    'type_from_name',
]
