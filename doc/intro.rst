.. include global.rst

Introduction
============

See the main libvips site for an introduction to the underlying library. These
notes introduce the Python binding.

https://libvips.github.io/libvips 

Example
-------

This example loads a file, boosts the green channel, sharpens the image,
and saves it back to disc again::

    import pyvips

    image = pyvips.Image.new_from_file('some-image.jpg', access='sequential')
    image *= [1, 2, 1]
    mask = pyvips.Image.new_from_list([[-1, -1, -1],
                                       [-1, 16, -1],
                                       [-1, -1, -1]
                                      ], scale=8)
    image = image.conv(mask, precision='integer')
    image.write_to_file('x.jpg')

Reading this example line by line, we have::

    image = pyvips.Image.new_from_file('some-image.jpg', access='sequential')

:meth:`.Image.new_from_file` can load any image file supported by libvips.
When you load an image, only the header is fetched from the file. Pixels will
not be read until you have built a pipeline of operations and connected it
to an output. 

When you load, you can hint what type of access you will need.  In this
example, we will be accessing pixels top-to-bottom as we sweep through
the image reading and writing, so `sequential` access mode is best for us.
The default mode is ``random`` which allows for full random access to image
pixels, but is slower and needs more memory. See :class:`.enums.Access`
for details on the various modes available.

You can also load formatted images from memory with
:meth:`.Image.new_from_buffer`, create images that wrap C-style memory arrays
held as Python buffers with :meth:`.Image.new_from_memory`, or make images
from constants with :meth:`.Image.new_from_list`. You can also create custom
sources and targets that link image processing pipelines to your own code,
see `Custom sources and targets`_.

The next line::

    image *= [1, 2, 1]

Multiplies the image by an array constant using one array element for each
image band. This line assumes that the input image has three bands and will
double the middle band. For RGB images, that's doubling green.

There is a full set arithmetic operator `Overloads`_, so you can compute with
entire images just as you would with single numbers.

Next we have::

    mask = pyvips.Image.new_from_list([[-1, -1, -1],
                                       [-1, 16, -1],
                                       [-1, -1, -1]
                                      ], scale = 8)
    image = image.conv(mask, precision = 'integer')

:meth:`.new_from_list` creates an image from a list of lists. The
scale is the amount to divide the image by after integer convolution.

See the libvips API docs for ``vips_conv()`` (the operation
invoked by :meth:`.Image.conv`) for details on the convolution operator. By
default, it computes with a float mask, but ``integer`` is fine for this case,
and is much faster.

Finally::

    image.write_to_file('x.jpg')

:meth:`.write_to_file` writes an image back to the filesystem. It can
write any format supported by vips: the file type is set from the filename
suffix. You can also write formatted images to memory, or dump
image data to a C-style array in a Python buffer.

Metadata and attributes
-----------------------

``pyvips`` adds a :meth:`.__getattr__` handler to :class:`.Image` and to
the Image metaclass, then uses it to look up unknown names in libvips.

Names are first checked against the set of properties that libvips
keeps for images, see :attr:`.width` and friends. If the name is not 
found there, ``pyvips`` searches the set of libvips operations, see the next 
section.

As well as the core properties, you can read and write the metadata
that libvips keeps for images with :meth:`.Image.get` and
friends. For example::

    image = pyvips.Image.new_from_file('some-image.jpg')
    ipct_string = image.get('ipct-data')
    exif_date_string = image.get('exif-ifd0-DateTime')

Use :meth:`.get_fields` to get a list of all the field names you can use with
:meth:`.Image.get`.

libvips caches and shares images between different parts of your program. This
means that you can't modify an image unless you are certain that you have
the only reference to it. You can make a private copy of an image with
``copy``, for example::

    new_image = image.copy(xres=12, yres=13)

Now ``new_image`` is a private clone of ``image`` with ``xres`` and ``yres``
changed.

Set image metadata with :meth:`.Image.set`. Use :meth:`.Image.copy` to make
a private copy of the image first, for example::

        new_image = image.copy().set('icc-profile-data', new_profile)

Now ``new_image`` is a clone of ``image`` with a new ICC profile attached to
it. 

NumPy and PIL
-------------

You can use :meth:`.new_from_array` to create a pyvips image from a NumPy array
or a PIL image. For example::

    import pyvips
    import numpy as np

    a = (np.random.random((100, 100, 3)) * 255).astype(np.uint8)
    image = pyvips.Image.new_from_array(a)

    import PIL.Image
    pil_image = PIL.Image.new('RGB', (60, 30), color = 'red')
    image = pyvips.Image.new_from_array(pil_image)

Going the other direction, a conversion from a pyvips image to a NumPy array can
be obtained with the :meth:`.numpy()` method of the :class:`pyvips.Image` class
or from the numpy side with :func:`numpy.asarray`.  This is a fast way to load
many image formats::

    import pyvips
    import numpy as np

    image = pyvips.Image.new_from_file('some-image.jpg')
    a1 = image.numpy()
    a2 = np.asarray(image)

    assert np.array_equal(a1, a2)
    
The :meth:`PIL.Image.fromarray` method can be used to convert a pyvips image
to a PIL image via a NumPy array::

    import pyvips
    import PIL.Image
    image = pyvips.Image.black(100, 100, bands=3)
    pil_image = PIL.Image.fromarray(image.numpy())


Calling libvips operations
--------------------------

Unknown names which are not image properties are looked up as libvips
operations. For example, the libvips operation ``add``, which appears in C as
``vips_add()``, appears in Python as :meth:`.Image.add`.

The operation's list of required arguments is searched and the first input
image is set to the value of ``self``. Operations which do not take an input
image, such as :meth:`.Image.black`, appear as class methods. The
remainder of the arguments you supply in the function call are used to set
the other required input arguments. Any trailing keyword arguments are used
to set options on the underlying libvips operation.

The result is the required output argument if there is only one result,
or a list of values if the operation produces several results. If the
operation has optional output objects, they are returned as a final
Python dictionary.

For example, :meth:`.Image.min`, the vips operation that searches an
image for the minimum value, has a large number of optional arguments. You
can use it to find the minimum value like this::

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
also a full set of arithmetic `Overloads`_.

libvips types are automatically wrapped. The binding looks at the type
of argument required by the operation and converts the value you supply,
when it can. For example, :meth:`.Image.linear` takes a
``VipsArrayDouble`` as an argument for the set of constants to use for
multiplication. You can supply this value as an integer, a float, or some
kind of compound object and it will be converted for you. You can write::

    result_image = image.linear(1, 3)
    result_image = image.linear(12.4, 13.9)
    result_image = image.linear([1, 2, 3], [4, 5, 6])
    result_image = image.linear(1, [4, 5, 6])

And so on. A set of overloads are defined for :meth:`.Image.linear`,
see below.

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

Logging and warnings
--------------------

The module uses ``logging`` to log warnings from libvips, and debug messages
from the module itself. Some warnings are important, for example truncated
files, and you might want to see them.

Add these lines somewhere near the start of your program::

        import logging
        logging.basicConfig(level=logging.WARNING)


Exceptions
----------

The wrapper spots errors from vips operations and raises the :class:`.Error`
exception. You can catch it in the usual way.

Enums
-----

The libvips enums, such as ``VipsBandFormat``, appear in pyvips as strings
like ``'uchar'``. They are documented as a set of classes for convenience, see
:class:`.Access`, for example.

Overloads
---------

The wrapper defines the usual set of arithmetic, boolean and relational
overloads on image. You can mix images, constants and lists of constants
freely. For example, you can write::

    result_image = ((image * [1, 2, 3]).abs() < 128) | 4

Expansions
----------

Some vips operators take an enum to select an action, for example
:meth:`.Image.math` can be used to calculate sine of every pixel
like this::

    result_image = image.math('sin')

This is annoying, so the wrapper expands all these enums into separate members
named after the enum value. So you can also write::

    result_image = image.sin()

Convenience functions
---------------------

The wrapper defines a few extra useful utility functions:
:meth:`.bandsplit`, :meth:`.maxpos`, :meth:`.minpos`,
:meth:`.median`.

Tracking and interrupting computation
-------------------------------------

You can attach progress handlers to images to watch the progress of
computation.

For example::

    image = pyvips.Image.black(1, 500)
    image.set_progress(True)
    image.signal_connect('preeval', preeval_handler)
    image.signal_connect('eval', eval_handler)
    image.signal_connect('posteval', posteval_handler)
    image.avg()

Handlers are given a `progress` object containing a number of useful fields.
For example::

   def eval_handler(image, progress):
       print('run time so far (secs) = {}'.format(progress.run))
       print('estimated time of arrival (secs) = {}'.format(progress.eta))
       print('total number of pels to process = {}'.format(progress.tpels))
       print('number of pels processed so far = {}'.format(progress.npels))
       print('percent complete = {}'.format(progress.percent))

Use :meth:`.Image.set_kill` on the image to stop computation early. 

For example::

   def eval_handler(image, progress):
       if progress.percent > 50:
           image.set_kill(True)

Custom sources and targets
--------------------------

You can load and save images to and from :class:`.Source` and
:class:`.Target`. 

For example::

   source = pyvips.Source.new_from_file("some/file/name")
   image = pyvips.Image.new_from_source(source, "", access="sequential")
   target = pyvips.Target.new_to_file("some/file/name")
   image.write_to_target(target, ".png")

Sources and targets can be files, descriptors (eg. pipes) and areas of memory.

You can define :class:`.SourceCustom` and :class:`.TargetCustom` too. 

For example::

   input_file = open(sys.argv[1], "rb")

   def read_handler(size):
       return input_file.read(size)

   source = pyvips.SourceCustom()
   source.on_read(read_handler)

   output_file = open(sys.argv[2], "wb")

   def write_handler(chunk):
       return output_file.write(chunk)

   target = pyvips.TargetCustom()
   target.on_write(write_handler)

   image = pyvips.Image.new_from_source(source, '', access='sequential')
   image.write_to_target(target, '.png')

You can also define seek and finish handlers, see the docs.

Automatic documentation
-----------------------

The bulk of these API docs are generated automatically by
:meth:`.Operation.generate_sphinx_all`. It examines libvips and writes a
summary of each operation and the arguments and options that that operation
expects.

Use the C API docs for more detail:

https://libvips.github.io/libvips/API/current

Draw operations
---------------

Paint operations like :meth:`.Image.draw_circle` and
:meth:`.Image.draw_line` modify their input image. This makes them
hard to use with the rest of libvips: you need to be very careful about
the order in which operations execute or you can get nasty crashes.

The wrapper spots operations of this type and makes a private copy of the
image in memory before calling the operation. This stops crashes, but it does
make it inefficient. If you draw 100 lines on an image, for example, you'll
copy the image 100 times. The wrapper does make sure that memory is recycled
where possible, so you won't have 100 copies in memory.

If you want to avoid the copies, you'll need to call drawing operations
yourself.

