from __future__ import division

import logging

from pyvips import ffi, gobject_lib

logger = logging.getLogger(__name__)


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
