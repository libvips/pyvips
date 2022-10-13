# basic defs and link to ffi


from pyvips import ffi, glib_lib, vips_lib, gobject_lib, \
    _to_string, _to_bytes, Error


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


def get_suffixes():
    """Get a list of all the filename suffixes supported by libvips.

    Returns:
        [string]

    """

    names = []

    if at_least_libvips(8, 8):
        array = vips_lib.vips_foreign_get_suffixes()
        i = 0
        while array[i] != ffi.NULL:
            name = _to_string(array[i])
            if name not in names:
                names.append(name)
            glib_lib.g_free(array[i])
            i += 1
        glib_lib.g_free(array)

    return names


# we need to define this before we import the declarations: they need to know
# which bits to make
def at_least_libvips(x, y):
    """Is this at least libvips x.y?"""

    major = version(0)
    minor = version(1)

    return major > x or (major == x and minor >= y)


def type_find(basename, nickname):
    """Get the GType for a name.

    Looks up the GType for a nickname. Types below basename in the type
    hierarchy are searched.
    """

    return vips_lib.vips_type_find(_to_bytes(basename), _to_bytes(nickname))


def type_name(gtype):
    """Return the name for a GType."""

    return _to_string(gobject_lib.g_type_name(gtype))


def nickname_find(gtype):
    """Return the nickname for a GType."""

    return _to_string(vips_lib.vips_nickname_find(gtype))


def type_from_name(name):
    """Return the GType for a name."""

    return gobject_lib.g_type_from_name(_to_bytes(name))


def type_map(gtype, fn):
    """Map fn over all child types of gtype."""

    cb = ffi.callback('VipsTypeMap2Fn', fn)
    return vips_lib.vips_type_map(gtype, cb, ffi.NULL, ffi.NULL)


def values_for_enum(gtype):
    """Get all values for a enum (gtype)."""

    g_type_class = gobject_lib.g_type_class_ref(gtype)
    g_enum_class = ffi.cast('GEnumClass *', g_type_class)

    # -1 since we always have a "last" member.
    return [_to_string(g_enum_class.values[i].value_nick)
            for i in range(g_enum_class.n_values - 1)]


def values_for_flag(gtype):
    """Get all values for a flag (gtype)."""

    g_type_class = gobject_lib.g_type_class_ref(gtype)
    g_flags_class = ffi.cast('GFlagsClass *', g_type_class)

    return [_to_string(g_flags_class.values[i].value_nick)
            for i in range(g_flags_class.n_values)]


__all__ = [
    'leak_set',
    'version',
    'at_least_libvips',
    'type_find',
    'nickname_find',
    'get_suffixes',
    'type_name',
    'type_map',
    'type_from_name',
    'values_for_enum',
    'values_for_flag'
]
