from __future__ import division

import logging

import pyvips
from pyvips import ffi, gobject_lib, _to_bytes

logger = logging.getLogger(__name__)

# the python marshallers for gobject signal handling

if pyvips.API_mode:
    @ffi.def_extern()
    def _marshall_image_progress(vi, pointer, handle):
        # the image we're passed is not reffed for us, so make a ref for us
        gobject_lib.g_object_ref(vi)
        image = pyvips.Image(vi)
        callback = ffi.from_handle(handle)
        progress = ffi.cast('VipsProgress*', pointer)
        callback(image, progress)
else:
    @ffi.callback("void(VipsImage*, void*, void*)")
    def _marshall_image_progress(vi, pointer, handle):
        # the image we're passed is not reffed for us, so make a ref for us
        gobject_lib.g_object_ref(vi)
        image = pyvips.Image(vi)
        callback = ffi.from_handle(handle)
        progress = ffi.cast('VipsProgress*', pointer)
        callback(image, progress)


class GObject(object):
    """Manage GObject lifetime.

    """

    def __init__(self, pointer):
        """Wrap around a pointer.

        Wraps a GObject instance around an underlying pointer. When the
        instance is garbage-collected, the underlying object is unreferenced.

        """

        # we have to record all of the ffi.new_handle we make for callbacks on
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

        The callback will be triggered every time this signal is issued on this
        instance. It will be passed the image ('self' here), and a single
        `void *` pointer from libvips. 
        
        The value of the pointer, if any, depends on the signal -- for
        example, ::eval passes a pointer to a `VipsProgress` struct.

        """

        go = ffi.cast('GObject *', self.pointer)
        handle = ffi.new_handle(callback)
        self._handles.append(handle)
        if pyvips.API_mode:
            marshall = gobject_lib._marshall_image_progress
        else:
            marshall = _marshall_image_progress

        gobject_lib.g_signal_connect_data(go, _to_bytes(name),
                                          ffi.cast('GCallback', marshall),
                                          handle,
                                          ffi.NULL, 0)


__all__ = ['GObject']
