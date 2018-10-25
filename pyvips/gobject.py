from __future__ import division

import logging

import pyvips
from pyvips import ffi, gobject_lib, _to_bytes

logger = logging.getLogger(__name__)


# the python marshallers for gobject signal handling

@ffi.callback("void(VipsImage*, void*, void*)")
def marshall_image_voidp(vi, progress, handle):
    image = pyvips.Image(vi)
    callback = ffi.from_handle(handle)
    callback(image, progress)


class GObject(object):
    """Manage GObject lifetime.

    """

    def __init__(self, pointer):
        """Wrap around a pointer.

        Wraps a GObject instance around an underlying pointer. When the
        instance is garbage-collected, the underlying object is unreferenced.

        """

        # we have t record all of the ffi.new_handle we make for callbacks on
        # this object to prevent them being GC'd
        self._handles = []

        # record the pointer we were given to manage
        self.pointer = pointer
        # logger.debug('GObject.__init__: pointer = %s', str(self.pointer))

        # on GC, unref
        self.gobject = ffi.gc(self.pointer, gobject_lib.g_object_unref)
        # logger.debug('GObject.__init__: gobject = %s', str(self.gobject))


    def signal_connect(self, name, callback):
        """Connect to a signal on this object.

        The closure will be triggered every time this signal is issued on this
        instance.
        """
        go = ffi.cast('GObject *', self.pointer)
        handle = ffi.new_handle(callback)
        self._handles.append(handle)
        marshall = ffi.cast('void(*)()', marshall_image_voidp)

        gobject_lib.g_signal_connect_data(go, _to_bytes(name), 
                                          marshall, handle, 
                                          ffi.NULL, 0)

__all__ = ['GObject']
