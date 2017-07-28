#!/usr/bin/env python

import sys

from cffi import FFI

ffi = FFI()

# possibly use ctypes.util.find_library() to locate the lib
# need a different name on windows? or os x?
# on win, may need to explcitly load other libraries as well
vips = ffi.dlopen('libvips.so')
gobject = ffi.dlopen('libgobject-2.0.so')

print('Loaded lib {0}'.format(vips))
print('Loaded lib {0}'.format(gobject))

# apparently the best way to find out
is_64bits = sys.maxsize > 2 ** 32

ffi.cdef('''
    int vips_init (const char* argv0);

    const char* vips_error_buffer (void);
    void vips_error_clear (void);
''')

def error(msg):
    print(msg)
    sys.exit(-1)

def vips_error():
    errstr = ffi.string(vips.vips_error_buffer())
    vips.vips_error_clear()

    error(errstr)

if vips.vips_init('') != 0:
    vips_error()

print('Inited libvips')

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
    typedef struct _GValue {
        GType gtype;
        uint64_t data[2]; 
    } GValue;

    typedef struct _VipsImage VipsImage;

    void* g_malloc(size_t size);
    void g_free(void* data);

    void g_object_ref (void* object);
    void g_object_unref (void* object);

    void g_value_init (GValue* value, GType gtype);
    void g_value_unset (GValue* value);
    const char* g_type_name (GType gtype);
    GType g_type_from_name (const char* name);
    GType g_type_fundamental (GType gtype);

    int vips_enum_from_nick (const char* domain, 
        GType gtype, const char* str);
    const char *vips_enum_nick (GType gtype, int value);

    void g_value_set_boolean (GValue* value, int v_boolean);
    void g_value_set_int (GValue* value, int i);
    void g_value_set_double (GValue* value, double d);
    void g_value_set_enum (GValue* value, int e);
    void g_value_set_flags (GValue* value, unsigned int f);
    void g_value_set_string (GValue* value, const char *str);
    void g_value_set_object (GValue* value, void* object);
    void vips_value_set_array_double (GValue* value, 
        const double* array, int n );
    void vips_value_set_array_int (GValue* value, 
        const int* array, int n );
    void vips_value_set_array_image (GValue *value, int n);
    void vips_value_set_blob (GValue* value,
            void (*free_fn)(void* data), void* data, size_t length);

    int g_value_get_boolean (const GValue* value);
    int g_value_get_int (GValue* value);
    double g_value_get_double (GValue* value);
    int g_value_get_enum (GValue* value);
    unsigned int g_value_get_flags (GValue* value);
    const char* g_value_get_string (GValue* value);
    const char* vips_value_get_ref_string (const GValue* value, size_t* length);
    void* g_value_get_object (GValue* value);
    double* vips_value_get_array_double (const GValue* value, int* n);
    int* vips_value_get_array_int (const GValue* value, int* n);
    VipsImage** vips_value_get_array_image (const GValue* value, int* n);
    void* vips_value_get_blob (const GValue* value, size_t* length);

    void vips_object_print_all (void);

''')

def print_all(msg):
    gc.collect()
    print(msg)
    vips.vips_object_print_all()
    print()

class GValue:

    # look up some common gtypes at init for speed
    gbool_type = gobject.g_type_from_name('gboolean')
    gint_type = gobject.g_type_from_name('gint')
    gdouble_type = gobject.g_type_from_name('gdouble')
    gstr_type = gobject.g_type_from_name('gchararray')
    genum_type = gobject.g_type_from_name('GEnum')
    gflags_type = gobject.g_type_from_name('GFlags')
    image_type = gobject.g_type_from_name('VipsImage')
    array_int_type = gobject.g_type_from_name('VipsArrayInt')
    array_double_type = gobject.g_type_from_name('VipsArrayDouble')
    array_image_type = gobject.g_type_from_name('VipsArrayImage')
    refstr_type = gobject.g_type_from_name('VipsRefString')
    blob_type = gobject.g_type_from_name('VipsBlob')

    @staticmethod
    def alloc():
        # memory will be freed on GC
        gvalue = ffi.new('GValue *')

        # and be unset
        gvalue = ffi.gc(gvalue, gobject.g_value_unset)

        return gvalue

    @staticmethod
    def type_name(gtype):
        return(ffi.string(gobject.g_type_name(gtype)))

    def init(self, gtype):
        gobject.g_value_init(self, gtype)

    def set(self, value):
        gtype = self.gtype
        fundamental = gobject.g_type_fundamental(gtype)

        if gtype == GValue.gbool_type:
            gobject.g_value_set_boolean(gv, value)
        else:
            error('unsupported gtype for set ' + self.type_name(gtype))

    def get(self):
        gtype = self.gtype
        fundamental = gobject.g_type_fundamental(gtype)

        if gtype == GValue.gbool_type:
            result = gobject.g_value_get_boolean(gv)
        else:
             error('unsupported gtype for get ' + gvalue.type_name(gtype))

        return result

gv = GValue.alloc()
gv.init(GValue.gbool_type)
gv.set(True)



