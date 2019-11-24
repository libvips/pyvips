from __future__ import division

import logging

import pyvips
from pyvips import ffi, gobject_lib, _to_bytes, Error, type_name

logger = logging.getLogger(__name__)

# the python marshalers for gobject signal handling
# - we keep a ref to each callback to stop them being GCd
# - I tried to make this less copy-paste, but failed -- check again

if pyvips.API_mode:
    @ffi.def_extern()
    def _marshal_image_progress(vi, pointer, handle):
        # the image we're passed is not reffed for us, so make a ref for us
        gobject_lib.g_object_ref(vi)
        image = pyvips.Image(vi)
        callback = ffi.from_handle(handle)
        progress = ffi.cast('VipsProgress*', pointer)
        callback(image, progress)
    _marshal_image_progress_cb = \
        ffi.cast('GCallback', gobject_lib._marshal_image_progress)
else:
    def _marshal_image_progress(vi, pointer, handle):
        # the image we're passed is not reffed for us, so make a ref for us
        gobject_lib.g_object_ref(vi)
        image = pyvips.Image(vi)
        callback = ffi.from_handle(handle)
        progress = ffi.cast('VipsProgress*', pointer)
        callback(image, progress)
    _marshal_image_progress_cb = \
        ffi.cast('GCallback',
                 ffi.callback('void(VipsImage*, void*, void*)',
                              _marshal_image_progress))

if pyvips.API_mode:
    @ffi.def_extern()
    def _marshal_read(streamiu, pointer, length, handle):
        buf = ffi.buffer(pointer, length)
        callback = ffi.from_handle(handle)
        return callback(streamiu, buf)
    _marshal_read_cb = \
        ffi.cast('GCallback', gobject_lib._marshal_read)
else:
    def _marshal_read(streamiu, pointer, length, handle):
        buf = ffi.buffer(pointer, length)
        callback = ffi.from_handle(handle)
        return callback(streamiu, buf)
    _marshal_read_cb = \
        ffi.cast('GCallback',
                 ffi.callback('gint64(VipsStreamiu*, void*, gint64, void*)',
                              _marshal_read))

if pyvips.API_mode:
    @ffi.def_extern()
    def _marshal_seek(streamiu, offset, whence, handle):
        callback = ffi.from_handle(handle)
        result = callback(streamiu, offset, whence)
        print(f'_marshal_seek: result = {result}')
        return result
    _marshal_seek_cb = \
        ffi.cast('GCallback', gobject_lib._marshal_seek)
else:
    def _marshal_seek(streamiu, offset, whence, handle):
        callback = ffi.from_handle(handle)
        return callback(streamiu, offset, whence)
    _marshal_seek_cb = \
        ffi.cast('GCallback',
                 ffi.callback('gint64(VipsStreamiu*, gint64, int, void*)',
                              _marshal_seek))

_marshalers = {
    "preeval": _marshal_image_progress_cb,
    "eval": _marshal_image_progress_cb,
    "posteval": _marshal_image_progress_cb,
    "read": _marshal_read_cb,
    "seek": _marshal_seek_cb,
}


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

    @staticmethod
    def new_pointer_from_gtype(gtype):
        """Make a new GObject pointer from a gtype.

        This is useful for subclasses which need to control the construction
        process. 
        
        You can pass the result pointer to the Python constructor for the 
        object you are building. You will need to call VipsObject.build() to
        finish construction.

        Returns:
            A pointer to a new GObject.

        Raises:
            :class:`.Error`

        """

        pointer = gobject_lib.g_object_new(gtype, ffi.NULL)
        if pointer == ffi.NULL:
            raise Error("can't create {0}".format(type_name(gtype)))

        return pointer

    def signal_connect(self, name, callback):
        """Connect to a signal on this object.

        The callback will be triggered every time this signal is issued on this
        instance. It will be passed the image ('self' here), and a single
        `void *` pointer from libvips.

        The value of the pointer, if any, depends on the signal -- for
        example, ::eval passes a pointer to a `VipsProgress` struct.

        """

        if name not in _marshalers:
            raise Error('unsupported signal "{0}"'.format(name))

        go = ffi.cast('GObject *', self.pointer)
        handle = ffi.new_handle(callback)
        self._handles.append(handle)

        gobject_lib.g_signal_connect_data(go, _to_bytes(name),
                                          _marshalers[name],
                                          handle, ffi.NULL, 0)


__all__ = ['GObject']
