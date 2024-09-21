# wrap VipsImage

import numbers
import struct

import pyvips
from pyvips import ffi, glib_lib, vips_lib, Error, _to_bytes, \
    _to_string, _to_string_copy, GValue, at_least_libvips, Introspect


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


# decorator to set docstring
def _add_doc(name):
    try:
        docstring = pyvips.Operation.generate_docstring(name)
    except Error:
        docstring = None

    def _doc(func):
        func.__doc__ = docstring
        return func

    return _doc


# decorator to set deprecated
def _deprecated(note):
    def _dep(func):
        func.__deprecated__ = note
        return func

    return _dep


# Rules for the mapping between numpy typestrings and libvips formats
# b1: bool. Above u1 so that rev. map is uchar->u1
TYPESTR_TO_FORMAT = {'|b1': 'uchar',
                     '|u1': 'uchar',
                     '|i1': 'char',
                     '<u2': 'ushort',
                     '<i2': 'short',
                     '<u4': 'uint',
                     '<i4': 'int',
                     '<f4': 'float',
                     '<c8': 'complex',
                     '<f8': 'double',
                     '<c16': 'dpcomplex'}

# Rules for the mapping between libvips formats and numpy typestrings
FORMAT_TO_TYPESTR = dict((v, k) for k, v in TYPESTR_TO_FORMAT.items())

# see https://docs.python.org/3/library/struct.html
FORMAT_TO_PYFORMAT = {'uchar': 'B',
                      'char': 'c',
                      'ushort': 'H',
                      'short': 'h',
                      'uint': 'I',
                      'int': 'i',
                      'float': 'f',
                      'double': 'd',
                      'complex': 'f',   # n.b. no support for complex in C
                      'dpcomplex': 'd'}


def _guess_interpretation(bands, format):
    """Return a best-guess interpretation string based on bands and libvips
    format.

    Args:
        bands (int): Number of bands in the image.
        format (str): libvips format string.

    Returns:
        str: the best-guess libvips interpretation string.

    This function is a helper for :class:`.Image` creation from arrays when the
    user specifies 'auto' for `interpretation`.

    The heuristic used here can be defined in the following table::

        | bands | format    | interpretation | reason       |
        | ----- | --------- | -------------- | ------------ |
        | 1     | uchar     | b-w            | L            |
        | 2     | uchar     | b-w            | LA           |
        | 3     | uchar     | rgb            | RGB          |
        | 4     | uchar     | rgb            | RGBA         |
        | 5+    | uchar     | multiband      | spectral     |
        | 1     | char      | matrix         | conv. kernel |
        | 2+    | char      | multiband      |              |
        | 1     | ushort    | grey16         | L            |
        | 2     | ushort    | grey16         | LA           |
        | 3     | ushort    | rgb16          | RGB          |
        | 4     | ushort    | rgb16          | RGBA         |
        | 5+    | ushort    | multiband      | spectral     |
        | any   | short     | multiband      |              |
        | 1     | float     | b-w            | L            |
        | 2     | float     | b-w            | LA           |
        | 3     | float     | scrgb          | RGB          |
        | 4     | float     | scrgb          | RGBA         |
        | 5+    | float     | multiband      | spectral     |
        | 1     | double    | b-w            | L            |
        | 2     | double    | b-w            | LA           |
        | 3     | double    | scrgb          | RGB          |
        | 4     | double    | scrgb          | RGBA         |
        | 5+    | double    | multiband      | spectral     |
        | any   | complex   | fourier        | FFT          |
        | any   | dpcomplex | fourier        | FFT          |

    """

    if format not in FORMAT_TO_TYPESTR:
        raise ValueError(f'Unknown format: {format}')
    if not isinstance(bands, int) or bands < 1:
        raise ValueError('Number of bands must be a positive integer.')

    # the default
    interp = 'multiband'

    if format == 'uchar':
        if bands in [1, 2]:
            interp = 'b-w'
        elif bands in [3, 4]:
            interp = 'rgb'
    elif format == 'char':
        if bands == 1:
            interp = 'matrix'
    elif format == 'ushort':
        if bands in [1, 2]:
            interp = 'grey16'
        elif bands in [3, 4]:
            interp = 'rgb16'
    elif format == 'short':
        if bands == 1:
            interp = 'matrix'
    elif format in ['float', 'double']:
        if bands in [1, 2]:
            interp = 'b-w'
        elif bands in [3, 4]:
            interp = 'scrgb'
    elif format in ['complex', 'dpcomplex']:
        interp = 'fourier'

    return interp


# metaclass for Image ... getattr on this implements the class methods
class ImageType(type):
    def __getattr__(cls, name):
        # logger.debug('ImageType.__getattr__ %s', name)

        # does the method exist in libvips?
        try:
            # this will throw an exception if not
            Introspect.get(name)
        except Error:
            # we need to throw this exception for missing methods, eg. numpy
            # checks for this
            raise AttributeError

        @_add_doc(name)
        def call_function(*args, **kwargs):
            return pyvips.Operation.call(name, *args, **kwargs)

        return call_function


class Image(pyvips.VipsObject, metaclass=ImageType):
    """Wrap a VipsImage object.

    """
    __slots__ = ('_references',)

    # private static

    @staticmethod
    def _imageize(self, value):
        # careful! self can be None if value is a 2D array
        if isinstance(value, Image):
            return value
        elif _is_2D(value):
            return Image.new_from_array(value)
        else:
            return self.new_from_image(value)

    def __init__(self, pointer):
        # a list of other objects which this object depends on and which need
        # to be kept alive
        # we can't use a set because set elements are unique under "==", and
        # Python checks memoryview equality with hash functions, not pointer
        # equality
        self._references = []
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
            vips_filename (str): The disc file to load the image from, with
                optional appended arguments.

        All loaders support at least the following options:

        Keyword args:
            memory (bool): If set True, load the image via memory rather than
                via a temporary disc file. See :meth:`.new_temp_file` for
                notes on where temporary files are created. Small images are
                loaded via memory by default, use ``VIPS_DISC_THRESHOLD`` to
                set the definition of small.
            access (Access): Hint the expected access pattern for the image.
            fail (bool): If set True, the loader will fail with an error on
                the first serious error in the file. By default, libvips
                will attempt to read everything it can from a damaged image.

        Returns:
            A new :class:`.Image`.

        Raises:
            :class:`.Error`

        """
        vips_filename = _to_bytes(vips_filename)
        pointer = vips_lib.vips_filename_get_filename(vips_filename)
        filename = _to_string_copy(pointer)

        pointer = vips_lib.vips_filename_get_options(vips_filename)
        options = _to_string_copy(pointer)

        pointer = vips_lib.vips_foreign_find_load(vips_filename)
        if pointer == ffi.NULL:
            raise Error(f'unable to load from file {vips_filename}')
        name = _to_string(pointer)

        return pyvips.Operation.call(name, filename,
                                     string_options=options, **kwargs)

    @staticmethod
    def new_from_buffer(data, options, **kwargs):
        """Load a formatted image from memory.

        This behaves exactly as :meth:`new_from_file`, but the image is
        loaded from the memory object rather than from a file. The memory
        object can be anything that supports the Python buffer protocol.

        Args:
            data (array, bytearray, bytes, buffer): The memory object to
                load the image from.
            options (str): Load options as a string. Use ``""`` for no options.

        All loaders support at least the following options:

        Keyword args:
            access (Access): Hint the expected access pattern for the image.
            fail (bool): If set True, the loader will fail with an error on the
                first serious error in the image. By default, libvips will
                attempt to read everything it can from a damaged image.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
        pointer = vips_lib.vips_foreign_find_load_buffer(data, len(data))
        if pointer == ffi.NULL:
            raise Error('unable to load from buffer')
        name = _to_string(pointer)

        return pyvips.Operation.call(name, data,
                                     string_options=options, **kwargs)

    @staticmethod
    def new_from_list(array, scale=1.0, offset=0.0):
        """Create an image from a list or list of lists.

        A new one-band image with :class:`BandFormat` ``'double'`` pixels is
        created from the array. These image are useful with the libvips
        convolution operator :meth:`Image.conv`.

        Args:
            array (list[list[float]]): Create the image from these values.
                1D arrays become a single row of pixels.
            scale (float): Default to 1.0. What to divide each pixel by after
                convolution.  Useful for integer convolution masks.
            offset (float): Default to 0.0. What to subtract from each pixel
                after convolution.  Useful for integer convolution masks.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
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

        image.set_type(GValue.gdouble_type, 'scale', scale)
        image.set_type(GValue.gdouble_type, 'offset', offset)

        return image

    @classmethod
    def new_from_array(cls, obj, scale=1.0, offset=0.0, interpretation=None):
        """Create a new Image from a list or an array-like object.

        Array-like objects are those which define `__array_interface__` or
        `__array__`. For details about the array interface, see `The Array
        Interface
        <https://numpy.org/doc/stable/reference/arrays.interface.html>`_.

        If `__array_interface__` is not available, `__array__` is used as a
        fallback.

        The behavior for input objects with different dimensions is summarized
        as::

            | array ndim | array shape | Image w | Image h | Image bands |
            |------------|-------------|---------|---------|-------------|
            | 0          | ()          | 1       | 1       | 1           |
            | 1          | (W,)        | W       | 1       | 1           |
            | 2          | (H, W)      | W       | H       | 1           |
            | 3          | (H, W, C)   | W       | H       | C           |


        Args:
            obj (list or object width `__array_interface__` or `__array__`):
                The object to convert to an image.

                If the input object is a list, `Image.new_from_list` is used
                with the given `scale` and `offset`

                If the input object is an array-like object, a new image is
                created from the object's data and shape.  The memory is shared
                except in the following cases:

                - The object's memory is not contiguous.  In this case, a copy
                  is made by attempting to call the object's `tobytes()` method
                  or its `tostring()` method.

                - The object is an array of bools, in which case it is
                  converted to a pyvips uchar image with True values becoming
                  255 and False values becoming 0.

            scale (float): Default to 1.0. **Ignored for non-list inputs**.
                What to divide each pixel by after convolution.  Useful for
                integer convolution masks.
            offset (float): Default to 0.0.  **Ignored for non-list inputs**.
                What to subtract from each pixel after convolution.  Useful for
                integer convolution masks.
            interpretation (str, optional): **Ignored for list inputs** The
                libvips interpretation of the array. If None, the
                interpretation defaults to the pyvips one for
                `Image.new_from_memory`.

                If 'auto', a heuristic is used to determine a best-guess
                interpretation as defined in the `_guess_interpretation`
                function.

                Must be one of None, 'auto', 'error', 'multiband', 'b-w',
                'histogram', 'xyz', 'lab', 'cmyk', 'labq', 'rgb', 'cmc', 'lch',
                'labs', 'srgb', 'yxy', 'fourier', 'rgb16', 'grey16', 'matrix',
                'scrgb', or 'hsv'

        Returns:
            The new image.

        See Also:
            :func:`_guess_interpretation`
        """
        if isinstance(obj, list):
            return cls.new_from_list(obj, scale, offset)

        if hasattr(obj, '__array_interface__'):
            a = obj.__array_interface__
            shape = a['shape']
            typestr = a['typestr']
            ndim = len(shape)

            # strides is optional
            strides = a.get('strides', None)

            if ndim > 3:
                raise ValueError('array has more than 3 dimensions')
            if typestr not in TYPESTR_TO_FORMAT:
                raise ValueError(f'conversion from {typestr} not supported')

            if ndim == 0:
                width = 1
                height = 1
                bands = 1
            elif ndim == 1:
                width = shape[0]
                height = 1
                bands = 1
            elif ndim == 2:
                height, width = shape
                bands = 1
            elif ndim == 3:
                height, width, bands = shape

            format = TYPESTR_TO_FORMAT[typestr]

            if strides is None and hasattr(obj, 'data'):
                data = obj.data
            else:
                # To obtain something with a contiguous memory layout
                if hasattr(obj, 'tobytes'):
                    data = obj.tobytes()
                elif hasattr(obj, 'tostring'):
                    data = obj.tostring()
                else:
                    raise TypeError('object has no .tobytes or .tostring')

            im = cls.new_from_memory(
                data,
                width,
                height,
                bands,
                format
            )

            if typestr == '|b1':
                # special case for bool: true in vips is uchar(255)
                im = im.ifthenelse(255, 0)

            if interpretation is not None:
                if interpretation == 'auto':
                    interpretation = _guess_interpretation(bands, format)

                im = im.copy(interpretation=interpretation)

            return im

        elif hasattr(obj, '__array__'):
            # make it into something that *does* define __array_interface__
            return cls.new_from_array(obj.__array__())
        else:
            raise TypeError('does not define __array_interface__ '
                            'or __array__')

    @staticmethod
    def new_from_memory(data, width, height, bands, format):
        """Wrap an image around a memory array.

        Wraps an Image around an area of memory containing a C-style array. For
        example, if the ``data`` memory array contains four bytes with the
        values 1, 2, 3, 4, you can make a one-band, 2x2 uchar image from
        it like this::

            image = Image.new_from_memory(data, 2, 2, 1, 'uchar')

        A reference is kept to the data object, so it will not be
        garbage-collected until the returned image is garbage-collected.

        This method is useful for efficiently transferring images from PIL or
        NumPy into libvips.

        See :meth:`.write_to_memory` for the opposite operation.

        Use :meth:`.copy` to set other image attributes.

        Args:
            data (bytes): A memoryview or buffer object.
            width (int): Image width in pixels.
            height (int): Image height in pixels.
            bands (int): Number of bands.
            format (BandFormat): Band format.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
        format_value = GValue.to_enum(GValue.format_type, format)
        pointer = ffi.from_buffer(data)
        nbytes = data.nbytes if hasattr(data, 'nbytes') else len(data)
        vi = vips_lib.vips_image_new_from_memory(pointer,
                                                 nbytes,
                                                 width, height, bands,
                                                 format_value)
        if vi == ffi.NULL:
            raise Error('unable to make image from memory')

        image = pyvips.Image(vi)

        # keep a secret ref to the underlying object .. this reference will be
        # inherited by things that in turn depend on us, so the memory we are
        # using will not be freed
        image._references.append(data)

        return image

    @staticmethod
    def new_from_source(source, options, **kwargs):
        """Load a formatted image from a source.

        This behaves exactly as :meth:`new_from_file`, but the image is
        loaded from the source rather than from a file.

        Args:
            source (Source): The source to load the image from.
            options (str): Load options as a string. Use ``""`` for no options.

        All loaders support at least the following options:

        Keyword args:
            access (Access): Hint the expected access pattern for the image.
            fail (bool): If set True, the loader will fail with an error on the
                first serious error in the image. By default, libvips will
                attempt to read everything it can from a damaged image.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
        pointer = vips_lib.vips_foreign_find_load_source(source.pointer)
        if pointer == ffi.NULL:
            raise Error('unable to load from source')
        name = _to_string(pointer)

        image = pyvips.Operation.call(name, source,
                                      string_options=options, **kwargs)

        # keep a secret ref to the source object .. we need that to stay
        # alive, since it might be a custom source that triggers a python
        # callback
        image._references.append(source)

        return image

    @staticmethod
    def new_temp_file(format):
        """Make a new temporary image.

        Returns an image backed by a temporary file. When written to with
        :func:`Image.write`, a temporary file will be created on disc in the
        specified format. When the image is closed, the file will be deleted
        automatically.

        The file is created in the temporary directory. This is set with
        the environment variable ``TMPDIR``. If this is not set, then on
        Unix systems, vips will default to ``/tmp``. On Windows, vips uses
        ``GetTempPath()`` to find the temporary directory.

        vips uses ``g_mkstemp()`` to make the temporary filename. They
        generally look something like ``"vips-12-EJKJFGH.v"``.

        Args:
            format (str): The format for the temp file, for example
                ``"%s.v"`` for a vips format file. The ``%s`` is
                substituted by the file path.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
        vi = vips_lib.vips_image_new_temp_file(_to_bytes(format))
        if vi == ffi.NULL:
            raise Error('unable to make temp file')

        return pyvips.Image(vi)

    def new_from_image(self, value):
        """Make a new image from an existing one.

        A new image is created which has the same size, format, interpretation
        and resolution as ``self``, but with every pixel set to ``value``.

        Args:
            value (float, list[float]): The value for the pixels. Use a
                single number to make a one-band image; use an array constant
                to make a many-band image.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
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
        """Copy an image to memory.

        A large area of memory is allocated, the image is rendered to that
        memory area, and a new image is returned which wraps that large memory
        area.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
        vi = vips_lib.vips_image_copy_memory(self.pointer)
        if vi == ffi.NULL:
            raise Error('unable to copy to memory')

        return pyvips.Image(vi)

    # writers

    def write_to_file(self, vips_filename, **kwargs):
        """Write an image to a file on disc.

        This method can save images in any format supported by vips. The format
        is selected from the filename suffix. The filename can include embedded
        save options, see :func:`Image.new_from_file`.

        For example::

            image.write_to_file('fred.jpg[Q=95]')

        You can also supply options as keyword arguments, for example::

            image.write_to_file('fred.jpg', Q=95)

        The full set of options available depend upon the load operation that
        will be executed. Try something like::

            $ vips jpegsave

        at the command-line to see a summary of the available options for the
        JPEG saver.

        Args:
            vips_filename (str): The disc file to save the image to, with
                optional appended arguments.

        Other arguments depend upon the save operation.

        Returns:
            None

        Raises:
            :class:`.Error`

        """
        vips_filename = _to_bytes(vips_filename)
        pointer = vips_lib.vips_filename_get_filename(vips_filename)
        filename = _to_string_copy(pointer)

        pointer = vips_lib.vips_filename_get_options(vips_filename)
        options = _to_string_copy(pointer)

        pointer = vips_lib.vips_foreign_find_save(vips_filename)
        if pointer == ffi.NULL:
            raise Error(f'unable to write to file {vips_filename}')
        name = _to_string(pointer)

        return pyvips.Operation.call(name, self, filename,
                                     string_options=options, **kwargs)

    def write_to_buffer(self, format_string, **kwargs):
        """Write an image to memory.

        This method can save images in any format supported by vips. The format
        is selected from the suffix in the format string. This can include
        embedded save options, see :func:`Image.write_to_file`.

        For example::

            data = image.write_to_buffer('.jpg[Q=95]')

        You can also supply options as keyword arguments, for example::

            data = image.write_to_buffer('.jpg', Q=95)

        The full set of options available depend upon the load operation that
        will be executed. Try something like::

            $ vips jpegsave_buffer

        at the command-line to see a summary of the available options for the
        JPEG saver.

        Args:
            format_string (str): The suffix, plus any string-form arguments.

        Other arguments depend upon the save operation.

        Returns:
            A byte string.

        Raises:
            :class:`.Error`

        """
        format_string = _to_bytes(format_string)

        filename = vips_lib.vips_filename_get_filename(format_string)
        filename = ffi.gc(filename, glib_lib.g_free)

        pointer = vips_lib.vips_filename_get_options(format_string)
        options = _to_string_copy(pointer)

        pointer = ffi.NULL
        if at_least_libvips(8, 9):
            vips_lib.vips_error_freeze()
            pointer = vips_lib.vips_foreign_find_save_target(filename)
            vips_lib.vips_error_thaw()

        if pointer != ffi.NULL:
            name = _to_string(pointer)
            target = pyvips.Target.new_to_memory()
            pyvips.Operation.call(name, self, target,
                                  string_options=options, **kwargs)
            buffer = target.get("blob")
        else:
            pointer = vips_lib.vips_foreign_find_save_buffer(filename)
            if pointer == ffi.NULL:
                raise Error('unable to write to buffer')

            name = _to_string(pointer)
            buffer = pyvips.Operation.call(name, self,
                                           string_options=options, **kwargs)

        return buffer

    def write_to_target(self, target, format_string, **kwargs):
        """Write an image to a target.

        This method will write the image to the target in the format
        specified in the suffix in the format string. This can include
        embedded save options, see :func:`Image.write_to_file`.

        For example::

            image.write_to_target(target, '.jpg[Q=95]')

        You can also supply options as keyword arguments, for example::

            image.write_to_target(target, '.jpg', Q=95)

        The full set of options available depend upon the save operation that
        will be executed. Try something like::

            $ vips jpegsave_target

        at the command-line to see a summary of the available options for the
        JPEG saver.

        Args:
            target (Target): The target to write the image to
            format_string (str): The suffix, plus any string-form arguments.

        Other arguments depend upon the save operation.

        Returns:
            None

        Raises:
            :class:`.Error`

        """
        format_string = _to_bytes(format_string)

        pointer = vips_lib.vips_filename_get_options(format_string)
        options = _to_string_copy(pointer)

        pointer = vips_lib.vips_foreign_find_save_target(format_string)
        if pointer == ffi.NULL:
            raise Error('unable to write to target')
        name = _to_string(pointer)

        return pyvips.Operation.call(name, self, target,
                                     string_options=options, **kwargs)

    def write_to_memory(self):
        """Write the image to a large memory array.

        A large area of memory is allocated, the image is rendered to that
        memory array, and the array is returned as a buffer.

        For example, if you have a 2x2 uchar image containing the bytes 1, 2,
        3, 4, read left-to-right, top-to-bottom, then::

            buf = image.write_to_memory()

        will return a four byte buffer containing the values 1, 2, 3, 4.

        Returns:
            buffer

        Raises:
            :class:`.Error`

        """
        psize = ffi.new('size_t *')
        pointer = vips_lib.vips_image_write_to_memory(self.pointer, psize)
        if pointer == ffi.NULL:
            raise Error('unable to write to memory')
        pointer = ffi.gc(pointer, glib_lib.g_free)

        return ffi.buffer(pointer, psize[0])

    def write(self, other):
        """Write an image to another image.

        This function writes ``self`` to another image. Use something like
        :func:`Image.new_temp_file` to make an image that can be written to.

        Args:
            other (Image): The :class:`Image` to write to,

        Returns:
            None

        Raises:
            :class:`.Error`

        """
        result = vips_lib.vips_image_write(self.pointer, other.pointer)
        if result != 0:
            raise Error('unable to write to image')

    def invalidate(self):
        """Drop caches on an image, and any downstream images.

        This method drops all pixel caches on an image and on all downstream
        images. Any operations which depend on this image, directly or
        indirectly, are also dropped from the libvips operation cache.

        This method can be useful if you wrap a libvips image around an area
        of memory with :meth:`.new_from_memory` and then change some bytes
        without libvips knowing.

        Returns:
            None

        """
        vips_lib.vips_image_invalidate_all(self.pointer)

    def set_progress(self, progress):
        """Enable progress reporting on an image.

        When progress reporting is enabled, evaluation of the most downstream
        image from this image will report progress using the ::preeval, ::eval,
        and ::posteval signals.

        """
        vips_lib.vips_image_set_progress(self.pointer, progress)

    def set_kill(self, kill):
        """Kill processing of an image.

        Use this to kill evaluation of an image. You can call it from one of
        the progress signals, for example. See :meth:`.set_progress`.

        """
        vips_lib.vips_image_set_kill(self.pointer, kill)

    # get/set metadata

    def get_typeof(self, name):
        """Get the GType of an item of metadata.

        Fetch the GType of a piece of metadata, or 0 if the named item does not
        exist. See :class:`GValue`.

        Args:
            name (str): The name of the piece of metadata to get the type of.

        Returns:
            The ``GType``, or 0.

        Raises:
            None

        """
        # on libvips before 8.5, property types must be fetched separately,
        # since built-in enums were reported as ints
        if not at_least_libvips(8, 5):
            gtype = super(Image, self).get_typeof(name)
            if gtype != 0:
                return gtype

        return vips_lib.vips_image_get_typeof(self.pointer, _to_bytes(name))

    def get(self, name):
        """Get an item of metadata.

        Fetches an item of metadata as a Python value. For example::

            orientation = image.get('orientation')

        would fetch the image orientation.

        Args:
            name (str): The name of the piece of metadata to get.

        Returns:
            The metadata item as a Python value.

        Raises:
            :class:`.Error`

        """
        # with old libvips, we must fetch properties (as opposed to
        # metadata) via VipsObject
        if not at_least_libvips(8, 5):
            gtype = super(Image, self).get_typeof(name)
            if gtype != 0:
                return super(Image, self).get(name)

        gv = GValue()
        result = vips_lib.vips_image_get(self.pointer, _to_bytes(name),
                                         gv.pointer)
        if result != 0:
            raise Error(f'unable to get {name}')

        return gv.get()

    def get_fields(self):
        """Get a list of all the metadata fields on an image.

        Returns:
            [string]

        """
        names = []

        if at_least_libvips(8, 5):
            array = vips_lib.vips_image_get_fields(self.pointer)
            i = 0
            while array[i] != ffi.NULL:
                name = _to_string(array[i])
                names.append(name)
                glib_lib.g_free(array[i])
                i += 1
            glib_lib.g_free(array)

        return names

    def set_type(self, gtype, name, value):
        """Set the type and value of an item of metadata.

        Sets the type and value of an item of metadata. Any old item of the
        same name is removed. See :class:`GValue` for types.

        Args:
            gtype (int): The GType of the metadata item to create.
            name (str): The name of the piece of metadata to create.
            value (mixed): The value to set as a Python value. It is
                converted to the ``gtype``, if possible.

        Returns:
            None

        Raises:
            None

        """
        gv = GValue()
        gv.set_type(gtype)
        gv.set(value)
        vips_lib.vips_image_set(self.pointer, _to_bytes(name), gv.pointer)

    def set(self, name, value):
        """Set the value of an item of metadata.

        Sets the value of an item of metadata. The metadata item must already
        exist.

        Args:
            name (str): The name of the piece of metadata to set the value of.
            value (mixed): The value to set as a Python value. It is
                converted to the type of the metadata item, if possible.

        Returns:
            None

        Raises:
            :class:`.Error`

        """
        gtype = self.get_typeof(name)
        if gtype == 0:
            raise Error(f'metadata item {name} does not exist -'
                        ' use set_type() to create and set')
        self.set_type(gtype, name, value)

    def remove(self, name):
        """Remove an item of metadata.

        The named metadata item is removed.

        Args:
            name (str): The name of the piece of metadata to remove.

        Returns:
            None

        Raises:
            None

        """
        return vips_lib.vips_image_remove(self.pointer, _to_bytes(name)) != 0

    def tolist(self):
        """Return a single-band image as a list of lists.

        Returns:
            list of lists of values

        """
        if not self.bands == 1:
            raise NotImplementedError('tolist only implemented for ' +
                                      'single-band images')

        is_complex = self.format in ['complex', 'dpcomplex']

        row_els = self.width if not is_complex else 2 * self.width

        rowfmt = f'{row_els}{FORMAT_TO_PYFORMAT[self.format]}'
        buf = self.write_to_memory()

        lst = [list(row) for row in struct.iter_unpack(rowfmt, buf)]

        if is_complex:
            lst = [[r[i] + 1j*r[i+1] for i in range(0, row_els, 2)]
                   for r in lst]

        return lst

    # Following will be relevant if we expose the buffer interface:
    # @property
    # def __array_interface__(self):
    #     """Return a numpy-standard __array_interface__ dictionary.
    #
    #     This is used by some libraries (PIL, e.g.) to interpret the image
    #     as an array.
    #
    #     See https://numpy.org/doc/stable/reference/arrays.interface.html for
    #     more info.
    #
    #     """
    #     if self.bands == 1:
    #         shape = (self.height, self.width)
    #     else:
    #         shape = (self.height, self.width, self.bands)
    #
    #     typestr = FORMAT_TO_TYPESTR[self.format]
    #
    #     interface = {
    #         'shape': shape,
    #         'strides': None,
    #         'descr': [('', typestr)],
    #         'typestr': typestr,
    #         'version': 3
    #     }
    #
    #     return interface

    def __array__(self, dtype=None):
        """Conversion to a NumPy array.

        Args:
            dtype (str or numpy dtype, optional) The dtype to use for the
                numpy array. If None, the default dtype of the image is used
                as defined the global `FORMAT_TO_TYPESTR` dictionary.

        Returns:
            numpy.ndarray: The array representation of the image.
                * Single-band images lose their channel axis.
                * Single-pixel single-band images are converted to a 0D array.

        See https://numpy.org/devdocs/user/basics.dispatch.html for more
        details.

        This enables a :class:`Image` to be used where a numpy array is
        expected, including in plotting and conversion to other array
        container types (pytorch, JAX, dask, etc.), for example.

        `numpy` is a runtime dependency of this function.

        See Also `Image.new_from_array` for the inverse operation. #TODO
        """
        import numpy as np

        arr = (
            np.frombuffer(self.write_to_memory(),
                          dtype=FORMAT_TO_TYPESTR[self.format])
            .reshape(self.height, self.width, self.bands)
        )

        if self.bands == 1:
            # flatten single-band images
            arr = arr.squeeze(axis=-1)

            if self.width == 1 and self.height == 1:
                # flatten single-pixel single-band images
                arr = arr.squeeze(axis=(0, 1))

        if dtype is not None:
            arr = arr.astype(dtype)

        return arr

    def numpy(self, dtype=None):
        """Convenience function to allow numpy conversion to be at the end
        of a method chain.

        This mimics the behavior of pytorch: ``arr = im.op1().op2().numpy()``

        numpy is a runtime dependency of this function.

        Args:
            dtype (str or numpy dtype): The dtype to use for the numpy array.
                If None, the default dtype of the image is used.

        Returns:
            numpy.ndarray: The image as a numpy array.

        See Also:

            - :meth:`.__array__`
            - `FORMAT_TO_TYPESTR`: Global dictionary mapping libvips format
              strings to numpy dtype strings.
        """
        return self.__array__(dtype=dtype)

    def __repr__(self):
        if (
            self.interpretation == "matrix"
            and self.width < 20
            and self.height < 20
            and self.bands == 1
        ):
            array = self.tolist()
            return repr(array)
        else:
            return (f'<pyvips.Image {self.width}x{self.height} {self.format}, '
                    f'{self.bands} bands, {self.interpretation}>')

    def __getattr__(self, name):
        """Divert unknown names to libvips.

        Unknown attributes are first looked up in the image properties as
        accessors, for example::

            width = image.width

        and then in the libvips operation table, where they become method
        calls, for example::

            new_image = image.invert()

        Use :func:`get` to fetch image metadata.

        A ``__getattr__`` on the metatype lets you call static members in the
        same way.

        Args:
            name (str): The name of the piece of metadata to get.

        Returns:
            Mixed.

        Raises:
            :class:`.Error`

        """
        # logger.debug('Image.__getattr__ %s', name)

        # scale and offset have default values
        if name == 'scale':
            if self.get_typeof('scale') != 0:
                return self.get('scale')
            else:
                return 1.0

        if name == 'offset':
            if self.get_typeof('offset') != 0:
                return self.get('offset')
            else:
                return 0.0

        # look up in props first (but not metadata)
        if super(Image, self).get_typeof(name) != 0:
            return super(Image, self).get(name)

        # does the method exist in libvips?
        try:
            # this will throw an exception if not
            Introspect.get(name)
        except Error:
            # we need to throw this exception for missing methods, eg. numpy
            # checks for this
            raise AttributeError

        @_add_doc(name)
        def call_function(*args, **kwargs):
            return pyvips.Operation.call(name, self, *args, **kwargs)

        return call_function

    # compatibility methods

    @_deprecated('use Image.get() instead')
    def get_value(self, name):
        return self.get(name)

    @_deprecated('use Image.set() instead')
    def set_value(self, name, value):
        self.set(name, value)

    @_deprecated('use Image.scale instead')
    def get_scale(self):
        return self.scale

    @_deprecated('use Image.offset instead')
    def get_offset(self):
        return self.offset

    # support with in the most trivial way

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getitem__(self, arg):
        """Overload [] to pull out band elements from an image.

        The following arguments types are accepted:

        * int::

            green = rgb_image[1]

          Will make a new one-band image from band 1 (the middle band).

        * slice::

            last_two = rgb_image[1:]
            last_band = rgb_image[-1]
            middle_few = multiband[1:-2]
            reversed  = multiband[::-1]
            every_other = multiband[::2]
            other_every_other = multiband[1::2]

        * list of int::

            # list of integers
            desired_bands = [1, 2, 2, -1]
            four_band = multiband[desired_bands]

        * list of bool::

            wanted_bands = [True, False, True, True, False]
            three_band = five_band[wanted_bands]

        In the case of integer or slice arguments, the semantics of slicing
        exactly match those of slicing `range(self.bands)`.

        In the case of list arguments, the semantics match those of numpy's
        extended slicing syntax. Thus, lists of booleans must have as many
        elements as there are bands in the image.

        """
        if isinstance(arg, int):
            # raises IndexError for bad integer indices
            i = range(self.bands)[arg]
            n = 1
        elif isinstance(arg, slice):
            band_seq = range(self.bands)[arg]
            if len(band_seq) == 0:
                raise IndexError('empty slice')

            i = band_seq[0]
            n = len(band_seq)
        elif isinstance(arg, list):
            if not arg:
                raise IndexError('empty list')

            # n.b. We don't use isinstance because isinstance(True, int)
            # is True!
            if not (all(type(x) == int for x in arg) or  # noqa: E721
                    all(type(x) == bool for x in arg)):  # noqa: E721
                raise IndexError('list must contain only ints or only bools')

            if isinstance(arg[0], bool):
                if len(arg) != self.bands:
                    raise IndexError('boolean index must have same ' +
                                     'length as bands')

                band_seq = [i for i, x in enumerate(arg) if x]
                n = len(band_seq)
                if n == 0:
                    raise IndexError('empty boolean index')
                if n == 1:
                    i = band_seq[0]
            else:
                all_bands = range(self.bands)
                # raises IndexError for bad int indices
                band_seq = [all_bands[i] for i in arg]

                n = len(band_seq)
                if n == 1:
                    i = band_seq[0]
        else:
            raise IndexError('argument must be an int, slice, ' +
                             'list of ints, or list of bools')

        if n == 1:
            # int or 1-element selection
            return self.extract_band(i)
        elif isinstance(arg, slice) and arg.step == 1:
            # sequential multi-band slice
            return self.extract_band(i, n=n)
        else:
            # nonsequential slice, list of ints, or list of bools
            bands = [self.extract_band(x) for x in band_seq]
            return bands[0].bandjoin(bands[1:])

    # overload () to mean fetch pixel
    def __call__(self, x, y):
        """Fetch a pixel value.

        Args:
            x (int): The x coordinate to fetch.
            y (int): The y coordinate to fetch.

        Returns:
            Pixel as an array of floating point numbers.

        Raises:
            :class:`.Error`

        """
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

        # guard against empty list
        if not other:
            return self

        # if [other] is all numbers, we can use bandjoin_const
        non_number = next((x for x in other
                           if not isinstance(x, numbers.Number)),
                          None)

        if non_number is None:
            return self.bandjoin_const(other)
        else:
            return pyvips.Operation.call('bandjoin', [self] + other)

    def atan2(self, other):
        return _call_enum(self, other, 'math2', 'atan2')

    def get_n_pages(self):
        """Get the number of pages in an image file, or 1.

        This is the number of pages in the file the image was loaded from, not
        the number of pages in the image.

        To get the number of pages in an image, divide the image height by
        the page height.
        """
        if at_least_libvips(8, 8):
            return vips_lib.vips_image_get_n_pages(self.pointer)
        else:
            return self.get("n-pages") \
                if self.get_typeof("n-pages") != 0 else 1

    def get_page_height(self):
        """Get the page height in a many-page image, or height.
        """
        if at_least_libvips(8, 8):
            return vips_lib.vips_image_get_page_height(self.pointer)
        else:
            if self.get_typeof("page-height") != 0:
                page_height = self.get("page-height")
            else:
                page_height = self.height

            if page_height > 0 and \
                page_height <= self.height and \
                    self.height % page_height == 0:
                return page_height
            else:
                return self.height

    def pagesplit(self):
        """Split an N-page image into a list of N separate images.
        """
        page_height = self.get_page_height()
        return [self.crop(0, y, self.width, page_height)
                for y in range(0, self.height, page_height)]

    def pagejoin(self, other):
        """Join a set of pages vertically to make a multipage image.

        Also sets the page-height property on the result.
        """
        if not isinstance(other, list):
            other = [other]

        n_pages = 1 + len(other)

        image = Image.arrayjoin([self] + other, across=1)
        image = image.copy()
        image.set_type(GValue.gint_type, 'page-height', image.height / n_pages)

        return image

    def composite(self, other, mode, **kwargs):
        """Composite a set of images with a set of modes."""
        if not isinstance(other, list):
            other = [other]
        if not isinstance(mode, list):
            mode = [mode]

        # modes are VipsBlendMode enums, but we have to pass as array of int --
        # we need to map str->int by hand
        mode = [GValue.to_enum(GValue.blend_mode_type, x) for x in mode]

        return pyvips.Operation.call('composite', [self] + other, mode,
                                     **kwargs)

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

    def sinh(self):
        """Return the hyperbolic sine of an image in radians."""
        return self.math('sinh')

    def cosh(self):
        """Return the hyperbolic cosine of an image in radians."""
        return self.math('cosh')

    def tanh(self):
        """Return the hyperbolic tangent of an image in radians."""
        return self.math('tanh')

    def asinh(self):
        """Return the inverse hyperbolic sine of an image in radians."""
        return self.math('asinh')

    def acosh(self):
        """Return the inverse hyperbolic cosine of an image in radians."""
        return self.math('acosh')

    def atanh(self):
        """Return the inverse hyperbolic tangent of an image in radians."""
        return self.math('atanh')

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

    def hasalpha(self):
        """True if the image has an alpha channel."""
        return vips_lib.vips_image_hasalpha(self.pointer)

    def addalpha(self):
        """Add an alpha channel."""
        if self.interpretation == 'grey16' or self.interpretation == 'rgb16':
            max_alpha = 65535
        elif self.interpretation == 'scrgb':
            max_alpha = 1.0
        else:
            max_alpha = 255
        return self.bandjoin(max_alpha)

    # we need different _imageize rules for this operator ... we need to
    # _imageize in1 and in2 to match each other first
    @_add_doc('ifthenelse')
    def ifthenelse(self, in1, in2, **kwargs):
        for match_image in [in1, in2, self]:
            if isinstance(match_image, pyvips.Image):
                break

        if not isinstance(in1, pyvips.Image):
            in1 = Image._imageize(match_image, in1)
        if not isinstance(in2, pyvips.Image):
            in2 = Image._imageize(match_image, in2)

        return pyvips.Operation.call('ifthenelse', self, in1, in2, **kwargs)

    def scaleimage(self, **kwargs):
        """Scale an image to 0 - 255.

        This is the libvips ``scale`` operation, renamed to avoid a clash with
        the ``scale`` for convolution masks.

        Keyword args:
            exp (float): Exponent for log scale.
            log (bool): Switch to turn on log scaling.

        Returns:
            A new :class:`Image`.

        Raises:
            :class:`.Error`

        """
        return pyvips.Operation.call('scale', self, **kwargs)


__all__ = ['Image']
