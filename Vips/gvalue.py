# wrap GValue

import numbers

from Vips import *

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

    // just for testing
    GType vips_interpretation_get_type (void);
    GType vips_operation_flags_get_type (void);

''')

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

    def __init__(self):
        # allocate memory for the gvalue which will be freed on GC
        self.memory = ffi.new('GValue *')
        log('GValue.__init__: memory = {0}'.format(self.memory))

        # and tag it to be unset on GC as well
        self.gvalue = ffi.gc(self.memory, gobject.g_value_unset)
        log('GValue.__init__: gvalue = {0}'.format(self.gvalue))

    @staticmethod
    def type_name(gtype):
        return(ffi.string(gobject.g_type_name(gtype)))

    def init(self, gtype):
        gobject.g_value_init(self.gvalue, gtype)

    def set(self, value):
        log('GValue.set: self = {0}, value = {1}'.format(self, value))

        gtype = self.gvalue.gtype
        fundamental = gobject.g_type_fundamental(gtype)

        if gtype == GValue.gbool_type:
            gobject.g_value_set_boolean(self.gvalue, value)
        elif gtype == GValue.gint_type:
            gobject.g_value_set_int(self.gvalue, value)
        elif gtype == GValue.gdouble_type:
            gobject.g_value_set_double(self.gvalue, value)
        elif fundamental == GValue.genum_type:
            if isinstance(value, basestring if is_PY2 else str):
                enum_value = vips.vips_enum_from_nick('pyvips', gtype, value)

                if enum_value < 0:
                    error('no such enum ' + value + '\n' + vips_get_error())
            else:
                enum_value = value

            gobject.g_value_set_enum(self.gvalue, enum_value)
        elif fundamental == GValue.gflags_type:
            gobject.g_value_set_flags(self.gvalue, value)
        elif gtype == GValue.gstr_type or gtype == GValue.refstr_type:
            gobject.g_value_set_string(self.gvalue, value)
        elif gtype == GValue.image_type:
            gobject.g_value_set_object(self.gvalue, value.vimage)
        elif gtype == GValue.array_int_type:
            if isinstance(value, numbers.Number):
                value = [value]

            array = ffi.new("int[]", value)
            vips.vips_value_set_array_int(self.gvalue, array, len(value))
        elif gtype == GValue.array_double_type:
            if isinstance(value, numbers.Number):
                value = [value]

            array = ffi.new("double[]", value)
            vips.vips_value_set_array_double(self.gvalue, array, len(value))
        elif gtype == GValue.array_image_type:
            if isinstance(value, Image):
                value = [value]

            # pull out all the VipsImage* pointers
            pointers = [x.vimage for x in value]

            # the gvalue needs a set of refs to own
            [vips.g_object_ref(x) for x in pointers]

            array = ffi.new("(VipsImage*)[]", pointers)
            vips.vips_value_set_array_double(self.gvalue, array, len(value))
        elif gtype == GValue.blob_type:
            # we need to set the blob to a copy of the string that vips
            # can own
            memory = glib.g_malloc(len(value))
            ffi.memcpy(memory, value, len(value))

            vips.vips_value_set_blob(self.gvalue, 
                    g_free_callback, memory, len(value))
        else:
            error('unsupported gtype for set ' + self.type_name(gtype))

    def get(self):
        log('GValue.get: self = {0}'.format(self))

        gtype = self.gvalue.gtype
        fundamental = gobject.g_type_fundamental(gtype)

        result = None

        if gtype == GValue.gbool_type:
            result = bool(gobject.g_value_get_boolean(self.gvalue))
        elif gtype == GValue.gint_type:
            result = gobject.g_value_get_int(self.gvalue)
        elif gtype == GValue.gdouble_type:
            result = gobject.g_value_get_double(self.gvalue)
        elif fundamental == GValue.genum_type:
            enum_value = gobject.g_value_get_enum(self.gvalue)

            cstr = vips.vips_enum_nick(gtype, enum_value)
            if cstr == 0:
                error("value not in enum")

            result = ffi.string(cstr)
        elif fundamental == GValue.gflags_type:
            result = gobject.g_value_get_flags(self.gvalue)
        elif gtype == GValue.gstr_type:
            cstr = gobject.g_value_get_string(self.gvalue)

            if cstr != ffi.NULL:
                result = ffi.string(cstr)
            else:
                result = nil
        elif gtype == GValue.refstr_type:
            psize = ffi.new("size_t *")

            cstr = vips.vips_value_get_ref_string(self.gvalue, psize)

            result = ffi.string(cstr, psize[0])
        elif gtype == GValue.image_type:
            # g_value_get_object() will not add a ref ... that is
            # held by the gvalue
            go = gobject.g_value_get_object(self.gvalue)
            vi = ffi.cast("VipsImage *", go)

            # we want a ref that will last with the life of the vimage: 
            # this ref is matched by the unref that's attached to finalize
            # by Image.new() 
            gobject.g_object_ref(go)

            result = Image.new(vi)
        elif gtype == GValue.array_int_type:
            pint = ffi.new("int *")

            array = vips.vips_value_get_array_int(self.gvalue, pint)
            result = []
            for i in range(0, pint[0]):
                result.append(array[i])
        elif gtype == GValue.array_double_type:
            pint = ffi.new("int *")

            array = vips.vips_value_get_array_double(self.gvalue, pint)
            result = []
            for i in range(0, pint[0]):
                result.append(array[i])
        elif gtype == GValue.array_image_type:
            pint = ffi.new("int *")

            array = vips.vips_value_get_array_image(self.gvalue, pint)
            result = []
            for i in range(0, pint[0]):
                # this will make a new cdata object 
                vi = array[i]

                result.append(Image.new(vi))
        elif gtype == GValue.blob_type:
            psize = ffi.new("size_t *")

            array = vips.vips_value_get_blob(self.gvalue, psize)
            result = ffi.string(array, psize[0])
        else:
             error('unsupported gtype for get ' + gvalue.type_name(gtype))

        return result
