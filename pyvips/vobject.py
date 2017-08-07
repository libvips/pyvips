# wrap VipsObject

from __future__ import division

import logging

from pyvips import *

logger = logging.getLogger(__name__)

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

    int vips_object_set_from_string (VipsObject* object, const char* options);

''')

class VipsObject(GObject):

    def __init__(self, pointer):
        # logger.debug('VipsObject.__init__: pointer = {0}'.format(pointer))
        super(VipsObject, self).__init__(pointer)

    @staticmethod
    def print_all(msg):
        gc.collect()
        logger.debug(msg)
        vips_lib.vips_object_print_all()
        logger.debug()

    # slow! eeeeew
    def get_typeof(self, name):
        # logger.debug('VipsObject.get_typeof: self = {0}, name = {1}'.
        #              format(self, name))

        pspec = ffi.new('GParamSpec **')
        argument_class = ffi.new('VipsArgumentClass **')
        argument_instance = ffi.new('VipsArgumentInstance **')
        vo = ffi.cast('VipsObject *', self.pointer)
        result = vips_lib.vips_object_get_argument(vo, to_bytes(name),
            pspec, argument_class, argument_instance)

        if result != 0:
            # need to clear any error, this is horrible
            Error('')
            return 0

        return pspec[0].value_type

    def get(self, name):
        logger.debug('VipsObject.get: self = {0}, name = {1}'.format(self, name))

        gtype = self.get_typeof(name)

        gv = GValue()
        gv.init(gtype)
        go = ffi.cast('GObject *', self.pointer)
        gobject_lib.g_object_get_property(go, to_bytes(name), gv.pointer)

        return gv.get()

    def set(self, name, value):
        logger.debug('VipsObject.set: self = {0}, name = {1}, value = {2}'.
            format(self, name, value))

        gtype = self.get_typeof(name)

        gv = GValue()
        gv.init(gtype)
        gv.set(value)
        go = ffi.cast('GObject *', self.pointer)
        gobject_lib.g_object_set_property(go, to_bytes(name), gv.pointer)

    # set a series of options using a string, perhaps 'fred=12, tile'
    def set_string(self, string_options):
        vo = ffi.cast('VipsObject *', self.pointer)
        result = vips_lib.vips_object_set_from_string(vo, 
                                                      to_bytes(string_options)) 

        return result == 0

__all__ = ['VipsObject']
