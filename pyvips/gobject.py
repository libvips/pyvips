from __future__ import division

import logging

from pyvips import ffi, gobject_lib

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
    """Manage GObject lifetime.

    """

    def __init__(self, pointer):
        """Wrap around a pointer.

        Wraps a GObject instance around an underlying pointer. When the
        instance is garbage-collected, the underlying object is unreferenced.

        """

        # record the pointer we were given to manage
        self.pointer = pointer
        # logger.debug('GObject.__init__: pointer = %s', str(self.pointer))

        # on GC, unref
        self.gobject = ffi.gc(self.pointer, gobject_lib.g_object_unref)
        # logger.debug('GObject.__init__: gobject = %s', str(self.gobject))


__all__ = ['GObject']
