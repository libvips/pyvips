# basic defs and link to ffi

from pyvips import ffi, vips_lib, gobject_lib, to_string, to_bytes

ffi.cdef('''
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


def leak_set(leak):
    """Enable or disable libvips leak checking.

    With this enabled, libvips will check for object and area leaks on exit.
    Enabling this option will make libvips run slightly more slowly.
    """
    return vips_lib.vips_leak_set(leak)


def path_filename7(filename):
    return to_string(ffi.string(vips_lib.vips_path_filename7(
        to_bytes(filename))))


def path_mode7(filename):
    return to_string(ffi.string(vips_lib.vips_path_mode7(to_bytes(filename))))


def type_find(basename, nickname):
    """Get the GType for a name.

    Looks up the GType for a nickname. Types below basename in the type
    hierarchy are searched.
    """
    return vips_lib.vips_type_find(to_bytes(basename), to_bytes(nickname))


def type_name(gtype):
    """Return the name for a GType.

    Looks up the name of a GType.
    """
    return to_string(ffi.string(gobject_lib.g_type_name(gtype)))


__all__ = [
    'leak_set',
    'path_filename7',
    'path_mode7',
    'type_find',
    'type_name',
]
