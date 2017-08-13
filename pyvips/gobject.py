from __future__ import division

import gc
import logging

from pyvips import ffi, vips_lib, gobject_lib

logger = logging.getLogger(__name__)

ffi.cdef('''
    typedef struct _GObject {
        void *g_type_instance;
        unsigned int ref_count;
        void *qdata;
    } GObject;

    typedef struct _GParamSpec {
        void* g_type_instance;

        const char* name;
        unsigned int flags;
        GType value_type;
        GType owner_type;

        // rest opaque
    } GParamSpec;

    void g_object_ref (void* object);
    void g_object_unref (void* object);

    void g_object_set_property (GObject* object,
        const char *name, GValue* value);
    void g_object_get_property (GObject* object,
        const char* name, GValue* value);

''')


class GObject(object):
    def __init__(self, pointer):
        # record the pointer we were given to manage
        self.pointer = pointer
        # logger.debug('GObject.__init__: pointer = %s', str(self.pointer))

        # on GC, unref
        self.gobject = ffi.gc(self.pointer, gobject_lib.g_object_unref)
        # logger.debug('GObject.__init__: gobject = %s', str(self.gobject))

    @staticmethod
    def print_all(msg):
        gc.collect()
        print(msg)
        vips_lib.vips_object_print_all()
        print()


__all__ = ['GObject']
