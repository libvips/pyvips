from __future__ import division

import logging

import pyvips
from pyvips import ffi, gobject_lib, _to_bytes, Error, type_name, \
    at_least_libvips

logger = logging.getLogger(__name__)

# the python marshalers for gobject signal handling
# - we keep a ref to each callback to stop them being GCd
# - I tried to make this less copy-paste, but failed -- check again

if pyvips.API_mode:
    @ffi.def_extern()
    def _marshal_image_progress(vi, pointer, handle):
        gobject_lib.g_object_ref(vi)
        image = pyvips.Image(vi)
        callback = ffi.from_handle(handle)
        progress = ffi.cast('VipsProgress*', pointer)
        callback(image, progress)
    _marshal_image_progress_cb =  \
        ffi.cast('GCallback', gobject_lib._marshal_image_progress)
else:
    @ffi.callback('void(VipsImage*, void*, void*)')
    def _marshal_image_progress(vi, pointer, handle):
        gobject_lib.g_object_ref(vi)
        image = pyvips.Image(vi)
        callback = ffi.from_handle(handle)
        progress = ffi.cast('VipsProgress*', pointer)
        callback(image, progress)
    _marshal_image_progress_cb = \
        ffi.cast('GCallback', _marshal_image_progress)

_marshalers = {
    'preeval': _marshal_image_progress_cb,
    'eval': _marshal_image_progress_cb,
    'posteval': _marshal_image_progress_cb,
}

if at_least_libvips(8, 9):
    if pyvips.API_mode:
        @ffi.def_extern()
        def _marshal_read(gobject, pointer, length, handle):
            buf = ffi.buffer(pointer, length)
            callback = ffi.from_handle(handle)
            return callback(buf)
        _marshal_read_cb = ffi.cast('GCallback', gobject_lib._marshal_read)
    else:
        @ffi.callback('gint64(VipsSourceCustom*, void*, gint64, void*)')
        def _marshal_read(gobject, pointer, length, handle):
            buf = ffi.buffer(pointer, length)
            callback = ffi.from_handle(handle)
            return callback(buf)
        _marshal_read_cb = ffi.cast('GCallback', _marshal_read)
    _marshalers['read'] = _marshal_read_cb

    if pyvips.API_mode:
        @ffi.def_extern()
        def _marshal_seek(gobject, offset, whence, handle):
            callback = ffi.from_handle(handle)
            return callback(offset, whence)
        _marshal_seek_cb = \
            ffi.cast('GCallback', gobject_lib._marshal_seek)
    else:
        @ffi.callback('gint64(VipsSourceCustom*, gint64, int, void*)')
        def _marshal_seek(gobject, offset, whence, handle):
            callback = ffi.from_handle(handle)
            return callback(offset, whence)
        _marshal_seek_cb = ffi.cast('GCallback', _marshal_seek)
    _marshalers['seek'] = _marshal_seek_cb

    if pyvips.API_mode:
        @ffi.def_extern()
        def _marshal_write(gobject, pointer, length, handle):
            buf = ffi.buffer(pointer, length)
            callback = ffi.from_handle(handle)
            return callback(buf)
        _marshal_write_cb = ffi.cast('GCallback', gobject_lib._marshal_write)
    else:
        @ffi.callback('gint64(VipsTargetCustom*, void*, gint64, void*)')
        def _marshal_write(gobject, pointer, length, handle):
            buf = ffi.buffer(pointer, length)
            callback = ffi.from_handle(handle)
            return callback(buf)
        _marshal_write_cb = ffi.cast('GCallback', _marshal_write)
    _marshalers['write'] = _marshal_write_cb

    if pyvips.API_mode:
        @ffi.def_extern()
        def _marshal_finish(gobject, handle):
            callback = ffi.from_handle(handle)
            callback()
        _marshal_finish_cb = ffi.cast('GCallback', gobject_lib._marshal_finish)
    else:
        @ffi.callback('void(VipsTargetCustom*, void*)')
        def _marshal_finish(gobject, handle):
            callback = ffi.from_handle(handle)
            callback()
        _marshal_finish_cb = ffi.cast('GCallback', _marshal_finish)
    _marshalers['finish'] = _marshal_finish_cb

if at_least_libvips(8, 13):
    if pyvips.API_mode:
        @ffi.def_extern()
        def _marshal_end(gobject, handle):
            callback = ffi.from_handle(handle)
            return callback()
        _marshal_end_cb = ffi.cast('GCallback', gobject_lib._marshal_end)
    else:
        @ffi.callback('int(VipsTargetCustom*, void*)')
        def _marshal_end(gobject, handle):
            callback = ffi.from_handle(handle)
            return callback()
        _marshal_end_cb = ffi.cast('GCallback', _marshal_end)
    _marshalers['end'] = _marshal_end_cb


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
        # we need to keep refs to the ffi handle and the callback to prevent
        # them being GCed
        # the callback might be a bound method (a closure) rather than a simple
        # function, so it can vanish
        self._handles.append(handle)
        self._handles.append(callback)

        gobject_lib.g_signal_connect_data(go, _to_bytes(name),
                                          _marshalers[name],
                                          handle, ffi.NULL, 0)


__all__ = ['GObject']
