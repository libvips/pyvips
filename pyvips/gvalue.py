# wrap GValue

from __future__ import division
from __future__ import unicode_literals 

import logging
import sys
import numbers

from pyvips import *

logger = logging.getLogger(__name__)

_is_PY2 = sys.version_info.major == 2

ffi.cdef('''
    typedef struct _GValue {
        GType gtype;
        uint64_t data[2]; 
    } GValue;

    void g_value_init (GValue* value, GType gtype);
    void g_value_unset (GValue* value);
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

class GValue(object):

    # look up some common gtypes at init for speed
    gbool_type = gobject_lib.g_type_from_name(b'gboolean')
    gint_type = gobject_lib.g_type_from_name(b'gint')
    gdouble_type = gobject_lib.g_type_from_name(b'gdouble')
    gstr_type = gobject_lib.g_type_from_name(b'gchararray')
    genum_type = gobject_lib.g_type_from_name(b'GEnum')
    gflags_type = gobject_lib.g_type_from_name(b'GFlags')
    gobject_type = gobject_lib.g_type_from_name(b'GObject')
    image_type = gobject_lib.g_type_from_name(b'VipsImage')
    array_int_type = gobject_lib.g_type_from_name(b'VipsArrayInt')
    array_double_type = gobject_lib.g_type_from_name(b'VipsArrayDouble')
    array_image_type = gobject_lib.g_type_from_name(b'VipsArrayImage')
    refstr_type = gobject_lib.g_type_from_name(b'VipsRefString')
    blob_type = gobject_lib.g_type_from_name(b'VipsBlob')

    def __init__(self):
        # allocate memory for the gvalue which will be freed on GC
        self.pointer = ffi.new('GValue *')
        # logger.debug('GValue.__init__: pointer = {0}'.format(self.pointer))

        # and tag it to be unset on GC as well
        self.gvalue = ffi.gc(self.pointer, gobject_lib.g_value_unset)
        # logger.debug('GValue.__init__: gvalue = {0}'.format(self.gvalue))

    def init(self, gtype):
        gobject_lib.g_value_init(self.gvalue, gtype)

    def set(self, value):
        # logger.debug('GValue.set: self = {0}, value = {1}'.format(self, value))

        gtype = self.gvalue.gtype
        fundamental = gobject_lib.g_type_fundamental(gtype)

        if gtype == GValue.gbool_type:
            gobject_lib.g_value_set_boolean(self.gvalue, value)
        elif gtype == GValue.gint_type:
            gobject_lib.g_value_set_int(self.gvalue, int(value))
        elif gtype == GValue.gdouble_type:
            gobject_lib.g_value_set_double(self.gvalue, value)
        elif fundamental == GValue.genum_type:
            if isinstance(value, basestring if _is_PY2 else str):
                enum_value = vips_lib.vips_enum_from_nick(b'pyvips', gtype, 
                                                          to_bytes(value))

                if enum_value < 0:
                    raise Error('no such enum {0}')
            else:
                enum_value = value

            gobject_lib.g_value_set_enum(self.gvalue, enum_value)
        elif fundamental == GValue.gflags_type:
            gobject_lib.g_value_set_flags(self.gvalue, value)
        elif gtype == GValue.gstr_type or gtype == GValue.refstr_type:
            gobject_lib.g_value_set_string(self.gvalue, to_bytes(value))
        elif fundamental == GValue.gobject_type:
            gobject_lib.g_value_set_object(self.gvalue, value.pointer)
        elif gtype == GValue.array_int_type:
            if isinstance(value, numbers.Number):
                value = [value]

            array = ffi.new('int[]', value)
            vips_lib.vips_value_set_array_int(self.gvalue, array, len(value))
        elif gtype == GValue.array_double_type:
            if isinstance(value, numbers.Number):
                value = [value]

            array = ffi.new('double[]', value)
            vips_lib.vips_value_set_array_double(self.gvalue, array, len(value))
        elif gtype == GValue.array_image_type:
            if isinstance(value, package_index['Image']):
                value = [value]

            vips_lib.vips_value_set_array_image(self.gvalue, len(value))
            array = vips_lib.vips_value_get_array_image(self.gvalue, ffi.NULL)
            for i, image in enumerate(value):
                vips_lib.g_object_ref(image.pointer)
                array[i] = image.pointer
        elif gtype == GValue.blob_type:
            # we need to set the blob to a copy of the string that vips_lib
            # can own
            memory = gobject_lib.g_malloc(len(value))
            ffi.memmove(memory, value, len(value))

            vips_lib.vips_value_set_blob(self.gvalue, 
                    gobject_lib.g_free, memory, len(value))
        else:
            raise Error('unsupported gtype for set {0}, fundamental {1}'.
                        format(type_name(gtype), type_name(fundamental)))

    def get(self):
        # logger.debug('GValue.get: self = {0}'.format(self))

        gtype = self.gvalue.gtype
        fundamental = gobject_lib.g_type_fundamental(gtype)

        result = None

        if gtype == GValue.gbool_type:
            result = bool(gobject_lib.g_value_get_boolean(self.gvalue))
        elif gtype == GValue.gint_type:
            result = gobject_lib.g_value_get_int(self.gvalue)
        elif gtype == GValue.gdouble_type:
            result = gobject_lib.g_value_get_double(self.gvalue)
        elif fundamental == GValue.genum_type:
            enum_value = gobject_lib.g_value_get_enum(self.gvalue)
            cstr = vips_lib.vips_enum_nick(gtype, enum_value)
            if cstr == 0:
                raise Error('value not in enum')

            result = to_string(ffi.string(cstr))
        elif fundamental == GValue.gflags_type:
            result = gobject_lib.g_value_get_flags(self.gvalue)
        elif gtype == GValue.gstr_type:
            cstr = gobject_lib.g_value_get_string(self.gvalue)

            if cstr != ffi.NULL:
                result = to_string(ffi.string(cstr))
        elif gtype == GValue.refstr_type:
            psize = ffi.new('size_t *')
            cstr = vips_lib.vips_value_get_ref_string(self.gvalue, psize)

            result = to_string(ffi.string(cstr, psize[0]))
        elif gtype == GValue.image_type:
            # g_value_get_object() will not add a ref ... that is
            # held by the gvalue
            go = gobject_lib.g_value_get_object(self.gvalue)
            vi = ffi.cast('VipsImage *', go)

            # we want a ref that will last with the life of the vimage: 
            # this ref is matched by the unref that's attached to finalize
            # by Image() 
            gobject_lib.g_object_ref(go)

            result = package_index['Image'](vi)
        elif gtype == GValue.array_int_type:
            pint = ffi.new('int *')
            array = vips_lib.vips_value_get_array_int(self.gvalue, pint)

            result = []
            for i in range(0, pint[0]):
                result.append(array[i])
        elif gtype == GValue.array_double_type:
            pint = ffi.new('int *')
            array = vips_lib.vips_value_get_array_double(self.gvalue, pint)

            result = []
            for i in range(0, pint[0]):
                result.append(array[i])
        elif gtype == GValue.array_image_type:
            pint = ffi.new('int *')
            array = vips_lib.vips_value_get_array_image(self.gvalue, pint)

            result = []
            for i in range(0, pint[0]):
                vi = array[i]
                vips_lib.g_object_ref(vi)
                image = package_index['Image'](vi)
                result.append(image)
        elif gtype == GValue.blob_type:
            psize = ffi.new('size_t *')
            array = vips_lib.vips_value_get_blob(self.gvalue, psize)
            buf = ffi.cast("char*", array)

            result = ffi.unpack(buf, psize[0])
        else:
             raise Error('unsupported gtype for get {0}'.
                         format(type_name(gtype)))

        return result

__all__ = ['GValue', 'type_find', 'type_name']
