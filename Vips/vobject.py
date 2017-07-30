# wrap VipsObject

from Vips import *

ffi.cdef('''
    typedef struct _VipsObject {
        GObject parent_object;
        bool constructed;
        bool static_object;
        void *argument_table;
        char *nickname;
        char *description;
        bool preclose;
        bool close;
        bool postclose;
        size_t local_memory;
    } VipsObject;

    typedef struct _VipsObjectClass VipsObjectClass;

    typedef struct _VipsArgument {
        GParamSpec *pspec;
    } VipsArgument;

    typedef struct _VipsArgumentInstance {
        VipsArgument parent;

        // opaque
    } VipsArgumentInstance;

    typedef enum _VipsArgumentFlags {
        VIPS_ARGUMENT_NONE = 0,
        VIPS_ARGUMENT_REQUIRED = 1,
        VIPS_ARGUMENT_CONSTRUCT = 2,
        VIPS_ARGUMENT_SET_ONCE = 4,
        VIPS_ARGUMENT_SET_ALWAYS = 8,
        VIPS_ARGUMENT_INPUT = 16,
        VIPS_ARGUMENT_OUTPUT = 32,
        VIPS_ARGUMENT_DEPRECATED = 64,
        VIPS_ARGUMENT_MODIFY = 128
    } VipsArgumentFlags;

    typedef struct _VipsArgumentClass {
        VipsArgument parent;

        VipsObjectClass *object_class;
        VipsArgumentFlags flags;
        int priority;
        uint64_t offset;
    } VipsArgumentClass;

    int vips_object_get_argument (VipsObject* object, 
        const char *name, GParamSpec** pspec, 
        VipsArgumentClass** argument_class,
        VipsArgumentInstance** argument_instance);

    void vips_object_print_all (void);

''')

class VipsObject(GObject):

    def __init__(self, pointer):
        log('VipsObject.__init__: pointer = {0}'.format(pointer))
        GObject.__init__(self, pointer)

    @staticmethod
    def print_all(msg):
        gc.collect()
        log(msg)
        vips_lib.vips_object_print_all()
        log()

    def get_typeof(self, name):
        log('VipsObject.get_typeof: self = {0}, name = {1}'.format(self, name))

        pspec = ffi.new("(GParamSpec *)[1]");
        argument_class = ffi.new("(VipsArgumentClass *)[1]");
        argument_instance = ffi.new("(VipsArgumentInstance *)[1]");
        result = vips_lib.vips_object_get_argument(self.gobject, name,
            pspec, argument_class, argument_instance)

        if result != 0:
            vips_error()

        return pspec[0].value_type

    def get(self, name):
        log('VipsObject.get: self = {0}, name = {1}'.format(self, name))

        gtype = self.get_typeof(name)

        gv = GValue()
        gv.init(gtype)
        gobject_lib.g_object_get_property(self.pointer, name, gv.pointer)

        return gv.get()

    def set(self, name, value):
        log('VipsObject.set: self = {0}, name = {1}, value = {2}'.format(self, name, value))

        gtype = self.get_typeof(name)

        gv = GValue()
        gv.init(gtype)
        gv.set(value)
        gobject_lib.g_object_set_property(self.pointer, name, gv.pointer)
