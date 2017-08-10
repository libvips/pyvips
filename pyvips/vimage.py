"""
:mod:`Image` -- An image
========================

.. module:: Image
    :synopsis: The base image class. 
.. moduleauthor:: John Cupitt <jcupitt@gmail.com>
.. moduleauthor:: Kleis Auke Wolthuizen <x@y.z>

This module defines the pyvips Image class. 

"""

from __future__ import division

import logging
import numbers

import pyvips
from pyvips import ffi, vips_lib, Error, to_bytes, to_string

logger = logging.getLogger(__name__)

ffi.cdef('''
    typedef struct _VipsImage {
        VipsObject parent_instance;

        // opaque
    } VipsImage;

    const char* vips_foreign_find_load (const char* name);
    const char* vips_foreign_find_load_buffer (const void* data, size_t size);
    const char* vips_foreign_find_save (const char* name);
    const char* vips_foreign_find_save_buffer (const char* suffix);

    VipsImage* vips_image_new_matrix_from_array (int width, int height,
            const double* array, int size);

    VipsImage* vips_image_copy_memory (VipsImage* image);

    GType vips_image_get_typeof (const VipsImage* image,
        const char* name);
    int vips_image_get (const VipsImage* image,
        const char* name, GValue* value_copy);
    void vips_image_set (VipsImage* image, const char* name, GValue* value);
    int vips_image_remove (VipsImage* image, const char* name);

    char* vips_filename_get_filename (const char* vips_filename);
    char* vips_filename_get_options (const char* vips_filename);

    VipsImage* vips_image_new_temp_file (const char* format);

    int vips_image_write (VipsImage* image, VipsImage* out);

''')


# either a single number, or a table of numbers
def _is_pixel(value):
    return (isinstance(value, numbers.Number) or
            (isinstance(value, list) and not
            isinstance(value, pyvips.Image)))


# test for rectangular array of something
def _is_2D(array):
    if not isinstance(array, list):
        return False

    for x in array:
        if not isinstance(x, list):
            return False
        if len(x) != len(array[0]):
            return False

    return True


# https://stackoverflow.com/a/22409540/1480019
def _with_metaclass(mcls):
    def decorator(cls):
        body = vars(cls).copy()
        # clean out class body
        body.pop('__dict__', None)
        body.pop('__weakref__', None)

        return mcls(cls.__name__, cls.__bases__, body)

    return decorator


# apply a function to a thing, or map over a list
# we often need to do something like (1.0 / other) and need to work for lists
# as well as scalars
def _smap(func, x):
    if isinstance(x, list):
        return list(map(func, x))
    else:
        return func(x)


def _call_enum(image, other, base, operation):
    if _is_pixel(other):
        return pyvips.Operation.call(base + '_const', image, operation, other)
    else:
        return pyvips.Operation.call(base, image, other, operation)


def _run_cmplx(fn, image):
    """Run a complex function on a non-complex image.

    The image needs to be complex, or have an even number of bands. The input
    can be int, the output is always float or double.
    """
    original_format = image.format

    if image.format != 'complex' and image.format != 'dpcomplex':
        if image.bands % 2 != 0:
            raise Error('not an even number of bands')

        if image.format != 'float' and image.format != 'double':
            image = image.cast('float')

        if image.format == 'double':
            new_format = 'dpcomplex'
        else:
            new_format = 'complex'

        image = image.copy(format=new_format, bands=image.bands / 2)

    image = fn(image)

    if original_format != 'complex' and original_format != 'dpcomplex':
        if image.format == 'dpcomplex':
            new_format = 'double'
        else:
            new_format = 'float'

        image = image.copy(format=new_format, bands=image.bands * 2)

    return image


# metaclass for Image ... getattr on this implements the class methods
class ImageType(type):
    def __getattr__(cls, name):
        # logger.debug('ImageType.__getattr__ %s', name)

        def call_function(*args, **kwargs):
            return pyvips.Operation.call(name, *args, **kwargs)

        return call_function


@_with_metaclass(ImageType)
class Image(pyvips.VipsObject):
    """The pyvips image class.

    This class represents a VipsImage object.

    """

    # private static

    @staticmethod
    def imageize(self, value):
        # careful! self can be None if value is a 2D array
        if isinstance(value, Image):
            return value
        elif _is_2D(value):
            return Image.new_from_array(value)
        else:
            return self.new_from_image(value)

    def __init__(self, pointer):
        # logger.debug('Image.__init__: pointer = %s', pointer)
        super(Image, self).__init__(pointer)

    # constructors

    @staticmethod
    def new_from_file(vips_filename, **kwargs):
        """Load an image from a file.

        This method can load images in any format supported by vips. The 
        filename can include load options, for example::

            image = pyvips.Image.new_from_file('fred.jpg[shrink=2]')

        You can also supply options as keyword arguments, for example::
        
            image = pyvips.Image.new_from_file('fred.jpg', shrink=2)

        The full set of options available depend upon the load operation that 
        will be executed. Try something like::
        
            $ vips jpegload
        
        at the command-line to see a summary of the available options for the
        JPEG loader.

        Loading is fast: only enough of the image is loaded to be able to fill
        out the header. Pixels will only be decompressed when they are needed.

        Args:
            ``vips_filename``: The disc file to load the image from, with
            optional appended arguments.

        All loaders support the following options:

        ``memory``:
            If set True, load the image via memory rather than via a temporary
            disc file. See temp_image_file for notes on where temporary files
            are created. Small images are loaded via memory by default, use
            VIPS_DISC_THRESHOLD to set the definition of small.
        ``access``:
            Hint the expected access pattern for the image, see :class:`Access`.
        ``fail``:
            If set True, the loader will fail with an error on the first serious 
            error in the file. By default, libvips will attempt to read 
            everything it can from a damanged image. 

        Returns:
            An :class:`Image`. 

        Raises:
            :class:`Error`

        """
        vips_filename = to_bytes(vips_filename)
        filename = vips_lib.vips_filename_get_filename(vips_filename)
        options = vips_lib.vips_filename_get_options(vips_filename)
        name = vips_lib.vips_foreign_find_load(filename)
        if name == ffi.NULL:
            raise Error('unable to load from file {0}'.format(vips_filename))

        return pyvips.Operation.call(to_string(ffi.string(name)),
                                     to_string(ffi.string(filename)),
                                     string_options=to_string(
                                         ffi.string(options)
                                     ), **kwargs)

    @staticmethod
    def new_from_buffer(data, options, **kwargs):
        """Load a formatted image from memory.
    
        This behaves as :func:`new_from_file`, but the image is loaded from the
        memory object rather than from a file. The memory object can be a string
        or buffer. 

        """
        name = vips_lib.vips_foreign_find_load_buffer(data, len(data))
        if name == ffi.NULL:
            raise Error('unable to load from buffer')

        return pyvips.Operation.call(to_string(ffi.string(name)), data,
                                     string_options=options, **kwargs)

    @staticmethod
    def new_from_array(array, scale=1.0, offset=0.0):
        if not _is_2D(array):
            array = [array]

        height = len(array)
        width = len(array[0])

        n = width * height
        a = ffi.new('double[]', n)
        for y in range(0, height):
            for x in range(0, width):
                a[x + y * width] = array[y][x]

        vi = vips_lib.vips_image_new_matrix_from_array(width, height, a, n)
        if vi == ffi.NULL:
            raise Error('unable to make image from matrix')
        image = pyvips.Image(vi)

        image.set_type(pyvips.GValue.gdouble_type, 'scale', scale)
        image.set_type(pyvips.GValue.gdouble_type, 'offset', offset)

        return image

    @staticmethod
    def new_temp_file(format):
        vi = vips_lib.vips_image_new_temp_file(to_bytes(format))
        if vi == ffi.NULL:
            raise Error('unable to make temp file')

        return pyvips.Image(vi)

    def new_from_image(self, value):
        pixel = (Image.black(1, 1) + value).cast(self.format)
        image = pixel.embed(0, 0, self.width, self.height,
                            extend='copy')
        image = image.copy(interpretation=self.interpretation,
                           xres=self.xres,
                           yres=self.yres,
                           xoffset=self.xoffset,
                           yoffset=self.yoffset)

        return image

    def copy_memory(self):
        vi = vips_lib.vips_image_copy_memory(self.pointer)
        if vi == ffi.NULL:
            raise Error('unable to copy to memory')

        return pyvips.Image(vi)

    # writers

    def write_to_file(self, vips_filename, **kwargs):
        """Write an image to a file on disc.

        The image is written to a file on disc. 

        """
        vips_filename = to_bytes(vips_filename)
        filename = vips_lib.vips_filename_get_filename(vips_filename)
        options = vips_lib.vips_filename_get_options(vips_filename)
        name = vips_lib.vips_foreign_find_save(filename)
        if name == ffi.NULL:
            raise Error('unable to write to file {0}'.format(vips_filename))

        return pyvips.Operation.call(to_string(ffi.string(name)), self,
                                     filename, string_options=to_string(
                                         ffi.string(options)
                                     ), **kwargs)

    def write_to_buffer(self, format_string, **kwargs):
        format_string = to_bytes(format_string)
        options = vips_lib.vips_filename_get_options(format_string)
        name = vips_lib.vips_foreign_find_save_buffer(format_string)
        if name == ffi.NULL:
            raise Error('unable to write to buffer')

        return pyvips.Operation.call(to_string(ffi.string(name)), self,
                                     string_options=to_string(
                                         ffi.string(options)
                                     ), **kwargs)

    def write(self, other):
        result = vips_lib.vips_image_write(self.pointer, other.pointer)
        if result != 0:
            raise Error('unable to write to image')

    # get/set metadata

    def get_typeof(self, name):
        return vips_lib.vips_image_get_typeof(self.pointer, to_bytes(name))

    def get(self, name):
        gv = pyvips.GValue()
        result = vips_lib.vips_image_get(self.pointer, to_bytes(name),
                                         gv.pointer)
        if result != 0:
            raise Error('unable to get {0}'.format(name))

        return gv.get()

    def set_type(self, gtype, name, value):
        gv = pyvips.GValue()
        gv.init(gtype)
        gv.set(value)
        vips_lib.vips_image_set(self.pointer, to_bytes(name), gv.pointer)

    def set(self, name, value):
        gtype = self.get_typeof(name)
        self.set_type(gtype, name, value)

    def remove(self, name):
        return vips_lib.vips_image_remove(self.pointer, to_bytes(name)) != 0

    def __getattr__(self, name):
        # logger.debug('Image.__getattr__ %s', name)

        # look up in props first (but not metadata)
        if super(Image, self).get_typeof(name) != 0:
            return super(Image, self).get(name)

        def call_function(*args, **kwargs):
            return pyvips.Operation.call(name, self, *args, **kwargs)

        return call_function

    # compatibility: these used to be called get_value / set_value
    get_value = get
    set_value = set

    # scale and offset with default values

    def get_scale(self):
        if self.get_typeof('scale') != 0:
            return self.get('scale')
        else:
            return 1.0

    def get_offset(self):
        if self.get_typeof('offset') != 0:
            return self.get('offset')
        else:
            return 0.0

    # support with in the most trivial way

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    # access as an array
    def __getitem__(self, arg):
        if isinstance(arg, slice):
            i = 0
            if arg.start is not None:
                i = arg.start

            n = self.bands - i
            if arg.stop is not None:
                if arg.stop < 0:
                    n = self.bands + arg.stop - i
                else:
                    n = arg.stop - i
        elif isinstance(arg, int):
            i = arg
            n = 1
        else:
            raise TypeError

        if i < 0:
            i = self.bands + i

        if i < 0 or i >= self.bands:
            raise IndexError

        return self.extract_band(i, n=n)

    # overload () to mean fetch pixel
    def __call__(self, x, y):
        return self.getpoint(x, y)

    # operator overloads

    def __add__(self, other):
        if isinstance(other, pyvips.Image):
            return self.add(other)
        else:
            return self.linear(1, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, pyvips.Image):
            return self.subtract(other)
        else:
            return self.linear(1, _smap(lambda x: -1 * x, other))

    def __rsub__(self, other):
        return self.linear(-1, other)

    def __mul__(self, other):
        if isinstance(other, Image):
            return self.multiply(other)
        else:
            return self.linear(other, 0)

    def __rmul__(self, other):
        return self.__mul__(other)

    # a / const has always been a float in vips, so div and truediv are the
    # same
    def __div__(self, other):
        if isinstance(other, pyvips.Image):
            return self.divide(other)
        else:
            return self.linear(_smap(lambda x: 1.0 / x, other), 0)

    def __rdiv__(self, other):
        return (self ** -1) * other

    def __truediv__(self, other):
        return self.__div__(other)

    def __rtruediv__(self, other):
        return self.__rdiv__(other)

    def __floordiv__(self, other):
        if isinstance(other, pyvips.Image):
            return self.divide(other).floor()
        else:
            return self.linear(_smap(lambda x: 1.0 / x, other), 0).floor()

    def __rfloordiv__(self, other):
        return ((self ** -1) * other).floor()

    def __mod__(self, other):
        if isinstance(other, pyvips.Image):
            return self.remainder(other)
        else:
            return self.remainder_const(other)

    def __pow__(self, other):
        return _call_enum(self, other, 'math2', 'pow')

    def __rpow__(self, other):
        return _call_enum(self, other, 'math2', 'wop')

    def __abs__(self):
        return self.abs()

    def __lshift__(self, other):
        return _call_enum(self, other, 'boolean', 'lshift')

    def __rshift__(self, other):
        return _call_enum(self, other, 'boolean', 'rshift')

    def __and__(self, other):
        return _call_enum(self, other, 'boolean', 'and')

    def __rand__(self, other):
        return self.__and__(other)

    def __or__(self, other):
        return _call_enum(self, other, 'boolean', 'or')

    def __ror__(self, other):
        return self.__or__(other)

    def __xor__(self, other):
        return _call_enum(self, other, 'boolean', 'eor')

    def __rxor__(self, other):
        return self.__xor__(other)

    def __neg__(self):
        return -1 * self

    def __pos__(self):
        return self

    def __invert__(self):
        return self ^ -1

    def __gt__(self, other):
        return _call_enum(self, other, 'relational', 'more')

    def __ge__(self, other):
        return _call_enum(self, other, 'relational', 'moreeq')

    def __lt__(self, other):
        return _call_enum(self, other, 'relational', 'less')

    def __le__(self, other):
        return _call_enum(self, other, 'relational', 'lesseq')

    def __eq__(self, other):
        # _eq version allows comparison to None
        if other is None:
            return False

        return _call_enum(self, other, 'relational', 'equal')

    def __ne__(self, other):
        # _eq version allows comparison to None
        if other is None:
            return True

        return _call_enum(self, other, 'relational', 'noteq')

    def floor(self):
        """Return the largest integral value not greater than the argument."""
        return self.round('floor')

    def ceil(self):
        """Return the smallest integral value not less than the argument."""
        return self.round('ceil')

    def rint(self):
        """Return the nearest integral value."""
        return self.round('rint')

    def bandand(self):
        """AND image bands together."""
        return self.bandbool('and')

    def bandor(self):
        """OR image bands together."""
        return self.bandbool('or')

    def bandeor(self):
        """EOR image bands together."""
        return self.bandbool('eor')

    def bandsplit(self):
        """Split an n-band image into n separate images."""
        return [x for x in self]

    def bandjoin(self, other):
        """Append a set of images or constants bandwise."""
        if not isinstance(other, list):
            other = [other]

        # if [other] is all numbers, we can use bandjoin_const
        non_number = next((x for x in other
                           if not isinstance(x, numbers.Number)),
                          None)

        if non_number is None:
            return self.bandjoin_const(other)
        else:
            return pyvips.Operation.call('bandjoin', [self] + other)

    def bandrank(self, other, **kwargs):
        """Band-wise rank filter a set of images."""
        if not isinstance(other, list):
            other = [other]

        return pyvips.Operation.call('bandrank', [self] + other, **kwargs)

    def maxpos(self):
        """Return the coordinates of the image maximum."""
        v, opts = self.max(x=True, y=True)
        x = opts['x']
        y = opts['y']
        return v, x, y

    def minpos(self):
        """Return the coordinates of the image minimum."""
        v, opts = self.min(x=True, y=True)
        x = opts['x']
        y = opts['y']
        return v, x, y

    def real(self):
        """Return the real part of a complex image."""
        return self.complexget('real')

    def imag(self):
        """Return the imaginary part of a complex image."""
        return self.complexget('imag')

    def polar(self):
        """Return an image converted to polar coordinates."""
        return _run_cmplx(lambda x: x.complex('polar'), self)

    def rect(self):
        """Return an image converted to rectangular coordinates."""
        return _run_cmplx(lambda x: x.complex('rect'), self)

    def conj(self):
        """Return the complex conjugate of an image."""
        return self.complex('conj')

    def sin(self):
        """Return the sine of an image in degrees."""
        return self.math('sin')

    def cos(self):
        """Return the cosine of an image in degrees."""
        return self.math('cos')

    def tan(self):
        """Return the tangent of an image in degrees."""
        return self.math('tan')

    def asin(self):
        """Return the inverse sine of an image in degrees."""
        return self.math('asin')

    def acos(self):
        """Return the inverse cosine of an image in degrees."""
        return self.math('acos')

    def atan(self):
        """Return the inverse tangent of an image in degrees."""
        return self.math('atan')

    def log(self):
        """Return the natural log of an image."""
        return self.math('log')

    def log10(self):
        """Return the log base 10 of an image."""
        return self.math('log10')

    def exp(self):
        """Return e ** pixel."""
        return self.math('exp')

    def exp10(self):
        """Return 10 ** pixel."""
        return self.math('exp10')

    def erode(self, mask):
        """Erode with a structuring element."""
        return self.morph(mask, 'erode')

    def dilate(self, mask):
        """Dilate with a structuring element."""
        return self.morph(mask, 'dilate')

    def median(self, size):
        """size x size median filter."""
        return self.rank(size, size, (size * size) / 2)

    def fliphor(self):
        """Flip horizontally."""
        return self.flip('horizontal')

    def flipver(self):
        """Flip vertically."""
        return self.flip('vertical')

    def rot90(self):
        """Rotate 90 degrees clockwise."""
        return self.rot('d90')

    def rot180(self):
        """Rotate 180 degrees."""
        return self.rot('d180')

    def rot270(self):
        """Rotate 270 degrees clockwise."""
        return self.rot('d270')

    # we need different imageize rules for this operator ... we need to
    # imageize th and el to match each other first
    def ifthenelse(self, th, el, **kwargs):
        for match_image in [th, el, self]:
            if isinstance(match_image, pyvips.Image):
                break

        if not isinstance(th, pyvips.Image):
            th = Image.imageize(match_image, th)
        if not isinstance(el, pyvips.Image):
            el = Image.imageize(match_image, el)

        return pyvips.Operation.call('ifthenelse', self, th, el, **kwargs)


__all__ = ['Image']
