from __future__ import division
from __future__ import unicode_literals

import logging
import numbers
import sys

import pyvips
from pyvips import ffi, vips_lib, gobject_lib, \
    glib_lib, Error, _to_bytes, _to_string, type_name, type_from_name, \
    at_least_libvips

logger = logging.getLogger(__name__)

_is_PY2 = sys.version_info.major == 2


class GValue(object):

    """Wrap GValue in a Python class.

    This class wraps :class:`.GValue` in a convenient interface. You can use
    instances of this class to get and set :class:`.GObject` properties.

    On construction, :class:`.GValue` is all zero (empty). You can pass it to
    a get function to have it filled by :class:`.GObject`, or use init to
    set a type, set to set a value, then use it to set an object property.

    GValue lifetime is managed automatically.

    """
    __slots__ = ('pointer', 'gvalue')

    # look up some common gtypes at init for speed
    gbool_type = type_from_name('gboolean')
    gint_type = type_from_name('gint')
    guint64_type = type_from_name('guint64')
    gdouble_type = type_from_name('gdouble')
    gstr_type = type_from_name('gchararray')
    genum_type = type_from_name('GEnum')
    gflags_type = type_from_name('GFlags')
    gobject_type = type_from_name('GObject')
    image_type = type_from_name('VipsImage')
    array_int_type = type_from_name('VipsArrayInt')
    array_double_type = type_from_name('VipsArrayDouble')
    array_image_type = type_from_name('VipsArrayImage')
    refstr_type = type_from_name('VipsRefString')
    blob_type = type_from_name('VipsBlob')
    source_type = type_from_name('VipsSource')
    target_type = type_from_name('VipsTarget')

    pyvips.vips_lib.vips_band_format_get_type()
    format_type = type_from_name('VipsBandFormat')

    if at_least_libvips(8, 6):
        pyvips.vips_lib.vips_blend_mode_get_type()
    blend_mode_type = type_from_name('VipsBlendMode')

    # map a gtype to the name of the corresponding Python type
    _gtype_to_python = {
        gbool_type: 'bool',
        gint_type: 'int',
        guint64_type: 'long',  # Note: int and long are unified in Python 3
        gdouble_type: 'float',
        gstr_type: 'str',
        refstr_type: 'str',
        genum_type: 'str',
        gflags_type: 'int',
        gobject_type: 'GObject',
        image_type: 'Image',
        array_int_type: 'list[int]',
        array_double_type: 'list[float]',
        array_image_type: 'list[Image]',
        blob_type: 'str',
        source_type: 'Source',
        target_type: 'Target',
    }

    @staticmethod
    def gtype_to_python(gtype):
        """Map a gtype to the name of the Python type we use to represent it.

        """

        fundamental = gobject_lib.g_type_fundamental(gtype)

        # enums can be strings or class members ... we want to generate a union
        # type
        if fundamental == GValue.genum_type:
            name = type_name(gtype)
            if name.startswith('Vips'):
                name = name[4:]
            return "Union[str, %s]" % name
        if gtype in GValue._gtype_to_python:
            return GValue._gtype_to_python[gtype]
        if fundamental in GValue._gtype_to_python:
            return GValue._gtype_to_python[fundamental]
        return '<unknown type>'

    @staticmethod
    def to_enum(gtype, value):
        """Turn a string into an enum value ready to be passed into libvips.

        """

        if isinstance(value, basestring if _is_PY2 else str):  # noqa: F821
            enum_value = vips_lib.vips_enum_from_nick(b'pyvips', gtype,
                                                      _to_bytes(value))
            if enum_value < 0:
                raise Error('no value {0} in gtype {1} ({2})'.
                            format(value, type_name(gtype), gtype))
        else:
            enum_value = value

        return enum_value

    @staticmethod
    def from_enum(gtype, enum_value):
        """Turn an int back into an enum string.

        """

        pointer = vips_lib.vips_enum_nick(gtype, enum_value)
        if pointer == ffi.NULL:
            raise Error('value not in enum')

        return _to_string(pointer)

    def __init__(self):
        # allocate memory for the gvalue which will be freed on GC
        self.pointer = ffi.new('GValue *')
        # logger.debug('GValue.__init__: pointer = %s', self.pointer)

        # and tag it to be unset on GC as well
        self.gvalue = ffi.gc(self.pointer, gobject_lib.g_value_unset)
        # logger.debug('GValue.__init__: gvalue = %s', self.gvalue)

    def set_type(self, gtype):
        """Set the type of a GValue.

        GValues have a set type, fixed at creation time. Use set_type to set
        the type of a GValue before assigning to it.

        GTypes are 32 or 64-bit integers (depending on the platform). See
        type_find.

        """

        gobject_lib.g_value_init(self.gvalue, gtype)

    def set(self, value):
        """Set a GValue.

        The value is converted to the type of the GValue, if possible, and
        assigned.

        """

        # logger.debug('GValue.set: value = %s', value)

        gtype = self.gvalue.g_type
        fundamental = gobject_lib.g_type_fundamental(gtype)

        if gtype == GValue.gbool_type:
            gobject_lib.g_value_set_boolean(self.gvalue, value)
        elif gtype == GValue.gint_type:
            gobject_lib.g_value_set_int(self.gvalue, int(value))
        elif gtype == GValue.guint64_type:
            gobject_lib.g_value_set_uint64(self.gvalue, value)
        elif gtype == GValue.gdouble_type:
            gobject_lib.g_value_set_double(self.gvalue, value)
        elif fundamental == GValue.genum_type:
            gobject_lib.g_value_set_enum(self.gvalue,
                                         GValue.to_enum(gtype, value))
        elif fundamental == GValue.gflags_type:
            gobject_lib.g_value_set_flags(self.gvalue, value)
        elif gtype == GValue.gstr_type:
            gobject_lib.g_value_set_string(self.gvalue, _to_bytes(value))
        elif gtype == GValue.refstr_type:
            vips_lib.vips_value_set_ref_string(self.gvalue, _to_bytes(value))
        elif fundamental == GValue.gobject_type:
            gobject_lib.g_value_set_object(self.gvalue, value.pointer)
        elif gtype == GValue.array_int_type:
            if isinstance(value, numbers.Number):
                value = [value]

            array = ffi.new('int[]', value)
            vips_lib.vips_value_set_array_int(self.gvalue, array, len(value))
        elif gtype == GValue.array_double_type:
            if isinstance(value, numbers.Number):
                value = [value]

            array = ffi.new('double[]', value)
            vips_lib.vips_value_set_array_double(self.gvalue, array,
                                                 len(value))
        elif gtype == GValue.array_image_type:
            if isinstance(value, pyvips.Image):
                value = [value]

            vips_lib.vips_value_set_array_image(self.gvalue, len(value))
            array = vips_lib.vips_value_get_array_image(self.gvalue, ffi.NULL)
            for i, image in enumerate(value):
                gobject_lib.g_object_ref(image.pointer)
                array[i] = image.pointer
        elif gtype == GValue.blob_type:
            # we need to set the blob to a copy of the string that vips_lib
            # can own
            memory = glib_lib.g_malloc(len(value))
            ffi.memmove(memory, value, len(value))

            # this is horrible!
            #
            # * in API mode, we must have 8.6+ and use set_blob_free to
            #   attach the metadata to avoid leaks
            # * pre-8.6, we just pass a NULL free pointer and live with the
            #   leak
            #
            # this is because in API mode you can't pass a builtin (what
            # vips_lib.g_free() becomes) as a parameter to ffi.callback(), and
            # vips_value_set_blob() needs a callback for arg 2
            #
            # additionally, you can't make a py def which calls g_free() and
            # then use the py def in the callback, since libvips will trigger
            # these functions during cleanup, and py will have shut down by
            # then and you'll get a segv

            if at_least_libvips(8, 6):
                vips_lib.vips_value_set_blob_free(self.gvalue,
                                                  memory, len(value))
            else:
                # we declare the type of the free func in set_blob incorrectly
                # so that we can pass g_free at runtime without triggering an
                # exception
                if pyvips.API_mode:
                    vips_lib.vips_value_set_blob(self.gvalue,
                                                 ffi.NULL, memory, len(value))
                else:
                    vips_lib.vips_value_set_blob(self.gvalue,
                                                 glib_lib.g_free,
                                                 memory, len(value))
        else:
            raise Error('unsupported gtype for set {0}, fundamental {1}'.
                        format(type_name(gtype), type_name(fundamental)))

    def get(self):
        """Get the contents of a GValue.

        The contents of the GValue are read out as a Python type.
        """

        # logger.debug('GValue.get: self = %s', self)

        gtype = self.gvalue.g_type
        fundamental = gobject_lib.g_type_fundamental(gtype)

        result = None

        if gtype == GValue.gbool_type:
            result = bool(gobject_lib.g_value_get_boolean(self.gvalue))
        elif gtype == GValue.gint_type:
            result = gobject_lib.g_value_get_int(self.gvalue)
        elif gtype == GValue.guint64_type:
            result = gobject_lib.g_value_get_uint64(self.gvalue)
        elif gtype == GValue.gdouble_type:
            result = gobject_lib.g_value_get_double(self.gvalue)
        elif fundamental == GValue.genum_type:
            return GValue.from_enum(gtype,
                                    gobject_lib.g_value_get_enum(self.gvalue))
        elif fundamental == GValue.gflags_type:
            result = gobject_lib.g_value_get_flags(self.gvalue)
        elif gtype == GValue.gstr_type:
            pointer = gobject_lib.g_value_get_string(self.gvalue)

            if pointer != ffi.NULL:
                result = _to_string(pointer)
        elif gtype == GValue.refstr_type:
            psize = ffi.new('size_t *')
            pointer = vips_lib.vips_value_get_ref_string(self.gvalue, psize)

            # psize[0] will be number of bytes in string, but just assume it's
            # NULL-terminated
            result = _to_string(pointer)
        elif gtype == GValue.image_type:
            # g_value_get_object() will not add a ref ... that is
            # held by the gvalue
            go = gobject_lib.g_value_get_object(self.gvalue)
            vi = ffi.cast('VipsImage *', go)

            # we want a ref that will last with the life of the vimage:
            # this ref is matched by the unref that's attached to finalize
            # by Image()
            gobject_lib.g_object_ref(vi)

            result = pyvips.Image(vi)
        elif gtype == GValue.array_int_type:
            pint = ffi.new('int *')
            array = vips_lib.vips_value_get_array_int(self.gvalue, pint)

            result = []
            for i in range(0, pint[0]):
                result.append(array[i])
        elif gtype == GValue.array_double_type:
            pint = ffi.new('int *')
            array = vips_lib.vips_value_get_array_double(self.gvalue, pint)

            result = []
            for i in range(0, pint[0]):
                result.append(array[i])
        elif gtype == GValue.array_image_type:
            pint = ffi.new('int *')
            array = vips_lib.vips_value_get_array_image(self.gvalue, pint)

            result = []
            for i in range(0, pint[0]):
                vi = array[i]
                gobject_lib.g_object_ref(vi)
                image = pyvips.Image(vi)
                result.append(image)
        elif gtype == GValue.blob_type:
            psize = ffi.new('size_t *')
            array = vips_lib.vips_value_get_blob(self.gvalue, psize)
            buf = ffi.cast('char*', array)

            result = ffi.unpack(buf, psize[0])
        else:
            raise Error('unsupported gtype for get {0}'.
                        format(type_name(gtype)))

        return result


__all__ = ['GValue']
