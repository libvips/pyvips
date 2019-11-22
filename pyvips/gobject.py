from __future__ import division

import logging

import pyvips
from pyvips import ffi, gobject_lib, _to_bytes

logger = logging.getLogger(__name__)

# the python marshalers for gobject signal handling
# we keep a ref to each callback to stop them being GCd

if pyvips.API_mode:
    @ffi.def_extern()
def _marshal_image_progress(vi, pointer, handle):
    # the image we're passed is not reffed for us, so make a ref for us
    gobject_lib.g_object_ref(vi)
    image = pyvips.Image(vi)
    callback = ffi.from_handle(handle)
    progress = ffi.cast('VipsProgress*', pointer)
    callback(image, progress)

if pyvips.API_mode:
    _marshal_image_progress_cb = \
        ffi.cast('GCallback', gobject_lib._marshal_image_progress)
else:
    _marshal_image_progress_cb = \
        ffi.cast('GCallback',
                 ffi.callback('void(VipsImage*, void*, void*)',
                              _marshal_image_progress))

if pyvips.API_mode:
    @ffi.def_extern()
def _marshal_read(streamiu, pointer, length, handle):
    buf = ffi.buffer(pointer, length)
    callback = ffi.from_handle(handle)
    callback(streamiu, buf)

if pyvips.API_mode:
    _marshal_read_cb = \
        ffi.cast('GCallback', gobject_lib._marshal_read)
else:
    _marshal_read_cb = \
        ffi.cast('GCallback',
                 ffi.callback('gint64(VipsStreamiu*, void*, gint64, void*)',
                              _marshal_read))

_marshalers = [
    "image_progress": _marshal_image_progress_cb,
    "read": _marshal_read_cb,
    "seek": _marshal_seek_cb,
]

if pyvips.API_mode:
    @ffi.def_extern()
def _marshal_seek(streamiu, offset, whence, handle):
    callback = ffi.from_handle(handle)
    callback(streamiu, offset, whence)

if pyvips.API_mode:
    _marshal_read_cb = \
        ffi.cast('GCallback', gobject_lib._marshal_seek)
else:
    _marshal_read_cb = \
        ffi.cast('GCallback',
                 ffi.callback('gint64(VipsStreamiu*, gint64, int, void*)',
                              _marshal_seek))


class GObject(object):
    """Manage GObject lifetime.

    """
    __slots__ = ('_handles', 'pointer')

    def __init__(self, pointer):
        """Wrap around a pointer.

        Wraps a GObject instance around an underlying pointer. When the
        instance is garbage-collected, the underlying object is unreferenced.

        """

        # we have to record all of the ffi.new_handle we make for callbacks on
        # this object to prevent them being GC'd
        self._handles = []

        # record the pointer we were given to manage
        # on GC, unref
        self.pointer = ffi.gc(pointer, gobject_lib.g_object_unref)
        # logger.debug('GObject.__init__: pointer = %s', str(self.pointer))

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

        gobject_lib.g_signal_connect_data(go, _to_bytes(name),
                                          _marshal_image_progress_cb,
                                          handle, ffi.NULL, 0)


__all__ = ['GObject']
