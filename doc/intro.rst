.. include global.rst

Introduction
============

This module wraps the libvips image processing library. It needs the libvips
shared library on your library search path, version 8.2 or later. 

See the main libvips site for an introduction to the underlying library. These
notes introduce the Python binding.

https://jcupitt.github.io/libvips 

Example
-------

This example loads a file, boosts the green channel, sharpens the image,
and saves it back to disc again::

    import pyvips

    image = pyvips.Image.new_from_file('some-image.jpg', access='sequential')
    image *= [1, 2, 1]
    mask = pyvips.Image.new_from_array([[-1, -1, -1],
                                        [-1, 16, -1],
                                        [-1, -1, -1]
                                       ], scale=8)
    image = image.conv(mask, precision='integer')
    image.write_to_file('x.jpg')

Reading this example line by line, we have::

    image = pyvips.Image.new_from_file('some-image.jpg', access='sequential')

:meth:`.new_from_file` can load any image file supported by libvips. In
this example, we will be accessing pixels top-to-bottom as we sweep through
the image reading and writing, so `sequential` access mode is best for us.

The default mode is ``random`` which allows for full random access to image
pixels, but is slower and needs more memory. See :class:`pyvips.enums.Access`
for full details on the various modes available.

You can also load formatted images from memory buffers, create images that
wrap C-style memory arrays, or make images from constants.

The next line::

    image *= [1, 2, 1]

Multiplying the image by an array constant uses one array element for each
image band. This line assumes that the input image has three bands and will
double the middle band. For RGB images, that's doubling green.

There are the usual range of arithmetic operator overloads.

Next we have::

    mask = pyvips.Image.new_from_array([[-1, -1, -1],
                                        [-1, 16, -1],
                                        [-1, -1, -1]
                                       ], scale = 8)
    image = image.conv(mask, precision = 'integer')

:meth:`.new_from_array` creates an image from an array constant. The
scale is the amount to divide the image by after integer convolution.

See the libvips API docs for ``vips_conv()`` (the operation
invoked by :meth:`.conv`) for details on the convolution operator. By
default, it computes with a float mask, but ``integer`` is fine for this case,
and is much faster.

Finally::

    image.write_to_file('x.jpg')

:meth:`.write_to_file` writes an image back to the filesystem. It can
write any format supported by vips: the file type is set from the filename
suffix. You can also write formatted images to memory buffers, or dump
image data to a raw memory array.

Automatic wrapping
------------------

``pyvips`` adds a :meth:`.__getattr__` handler to :class:`.Image`
and to the Image metaclass, then uses it to look up vips operations. For
example, the libvips operation ``add``, which appears in C as ``vips_add()``,
appears in Python as :meth:`.add`.

The operation's list of required arguments is searched and the first input
image is set to the value of ``self``. Operations which do not take an input
image, such as :meth:`.black`, appear as class methods. The remainder of
the arguments you supply in the function call are used to set the other
required input arguments. Any trailing keyword arguments are used to set
options on the operation.

The result is the required output argument if there is only one result,
or an array of values if the operation produces several results. If the
operation has optional output objects, they are returned as a final hash.

For example, :meth:`.min`, the vips operation that searches an image for
the minimum value, has a large number of optional arguments. You can use it to
find the minimum value like this::

    min_value = image.min()

You can ask it to return the position of the minimum with `:x` and `:y`::

    min_value, opts = image.min(x=True, y=True)
    x_pos = opts['x']
    y_pos = opts['y']

Now ``x_pos`` and ``y_pos`` will have the coordinates of the minimum value.
There's actually a convenience method for this, :meth:`.minpos`.

You can also ask for the top *n* minimum, for example::

    min_value, opts = min(size=10, x_array=True, y_array=True)
    x_pos = opts['x_array']
    y_pos = opts['y_array']

Now ``x_pos`` and ``y_pos`` will be 10-element arrays.

Because operations are member functions and return the result image, you can
chain them. For example, you can write::

    result_image = image.real().cos()

to calculate the cosine of the real part of a complex image.  There is
also a full set of arithmetic operator overloads, see below.

libvips types are automatically wrapped. The binding looks at the type
of argument required by the operation and converts the value you supply,
when it can. For example, :meth:`.linear` takes a ``VipsArrayDouble`` as an
argument for the set of constants to use for multiplication. You can supply
this value as an integer, a float, or some kind of compound object and it
will be converted for you. You can write::

    result_image = image.linear(1, 3)
    result_image = image.linear(12.4, 13.9)
    result_image = image.linear([1, 2, 3], [4, 5, 6])
    result_image = image.linear(1, [4, 5, 6])

And so on. A set of overloads are defined for :meth:`.linear`, see below.

It also does a couple of more ambitious conversions. It will automatically
convert to and from the various vips types, like ``VipsBlob`` and
``VipsArrayImage``. For example, you can read the ICC profile out of an
image like this::

    profile = im.get('icc-profile-data')

and profile will be a byte string.

If an operation takes several input images, you can use a constant for all but
one of them and the wrapper will expand the constant to an image for you. For
example, :meth:`.ifthenelse` uses a condition image to pick pixels
between a then and an else image::

    result_image = condition_image.ifthenelse(then_image, else_image)

You can use a constant instead of either the then or the else parts and it
will be expanded to an image for you. If you use a constant for both then and
else, it will be expanded to match the condition image. For example::

    result_image = condition_image.ifthenelse([0, 255, 0], [255, 0, 0])

Will make an image where true pixels are green and false pixels are red.

This is useful for :meth:`.bandjoin`, the thing to join two or more
images up bandwise. You can write::

    rgba = rgb.bandjoin(255)

to append a constant 255 band to an image, perhaps to add an alpha channel. Of
course you can also write::

    result_image = image1.bandjoin(image2)
    result_image = image1.bandjoin([image2, image3])
    result_image = pyvips.Image.bandjoin([image1, image2, image3])
    result_image = image1.bandjoin([image2, 255])

and so on.

Automatic documentation
-----------------------

The bulk of these API docs are generated automatically by
:meth:`.Operation.generate_sphinx_all`. It examines libvips and writes a
summary of each operation and the arguments and options that that operation
expects.

Use the C API docs for more detail:

https://jcupitt.github.io/libvips/API/current

Exceptions
----------

The wrapper spots errors from vips operations and raises the :class:`.Error`
exception. You can catch it in the usual way.

Enums
-----

The libvips enums, such as ``VipsBandFormat``, appear in pyvips as strings
like ``'uchar'``. They are documented as a set of classes for convenience, see
:class:`.Access`, for example.

Draw operations
---------------

Paint operations like :meth:`.draw_circle` and :meth:`.draw_line`
modify their input image. This makes them hard to use with the rest of
libvips: you need to be very careful about the order in which operations
execute or you can get nasty crashes.

The wrapper spots operations of this type and makes a private copy of the
image in memory before calling the operation. This stops crashes, but it does
make it inefficient. If you draw 100 lines on an image, for example, you'll
copy the image 100 times. The wrapper does make sure that memory is recycled
where possible, so you won't have 100 copies in memory.

If you want to avoid the copies, you'll need to call drawing operations
yourself.

Overloads
---------

The wrapper defines the usual set of arithmetic, boolean and relational
overloads on image. You can mix images, constants and lists of constants
freely. For example, you can write::

    result_image = ((image * [1, 2, 3]).abs() < 128) | 4

Expansions
----------

Some vips operators take an enum to select an action, for example
:meth:`.math` can be used to calculate sine of every pixel like this::

    result_image = image.math('sin')

This is annoying, so the wrapper expands all these enums into separate members
named after the enum value. So you can also write::

    result_image = image.sin()

Convenience functions
---------------------

The wrapper defines a few extra useful utility functions:
:meth:`.bandsplit`, :meth:`.maxpos`, :meth:`.minpos`,
:meth:`.median`.

