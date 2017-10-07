README
======

.. image:: https://travis-ci.org/jcupitt/pyvips.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/jcupitt/pyvips

PyPI package:

https://pypi.python.org/pypi/pyvips

This module wraps the libvips image processing library. It needs the libvips
shared library on your library search path, version 8.2 or later. 

https://jcupitt.github.io/libvips

This binding passes the vips test suite cleanly and with no leaks under
python2.7 - python3.6, pypy and pypy3 on Windows, macOS and Linux. 

We have formatted docs online here:

https://jcupitt.github.io/pyvips/

How it works
------------

Programs that use ``pyvips`` don't manipulate images directly, instead
they create pipelines of image processing operations building on a source
image. When the end of the pipe is connected to a destination, the whole
pipeline executes at once, streaming the image in parallel from source to
destination a section at a time.

Because ``pyvips`` is parallel, it's quick, and because it doesn't need to
keep entire images in memory, it's light.  For example, the libvips 
speed and memory use benchmark: 

https://github.com/jcupitt/libvips/wiki/Speed-and-memory-use

Loads a large tiff image, shrinks by 10%, sharpens, and saves again. On this
test ``pyvips`` is typically 5x faster than Pillow-SIMD and needs 4x less
memory. 

There's a handy blog post explaining how libvips opens files, which gives
some more background.

http://libvips.blogspot.co.uk/2012/06/how-libvips-opens-file.html

Install
-------

You need the libvips shared library on your library search path, version 8.2 or
later. On linux and macOS, you can install via your package manager; on 
Windows you can download a pre-compiled binary from the libvips website:

https://jcupitt.github.io/libvips/

Then just install this package, perhaps::

	$ pip install --user pyvips

Example
-------

This sample program loads a JPG image, doubles the value of every green pixel,
sharpens, and then writes the image back to the filesystem again::

    import pyvips

    image = pyvips.Image.new_from_file('some-image.jpg', access='sequential')
    image *= [1, 2, 1]
    mask = pyvips.Image.new_from_array([[-1, -1, -1],
                                        [-1, 16, -1],
                                        [-1, -1, -1]
                                       ], scale=8)
    image = image.conv(mask, precision='integer')
    image.write_to_file('x.jpg')

Converting old code
-------------------

To convert old code, replace the lines::

	import gi
	gi.require_version('Vips', '8.0')
	from gi.repository import Vips 

with::

	import pyvips
	Vips = pyvips

Instead of the ``pyvips = Vips``, you can of course also swap all ``Vips`` for
``pyvips`` with eg.::

        %s/Vips/pyvips/g

Background
----------

The Python binding included in libvips works, but porting and installation
are more difficult than they should be. 

This new binding is:

* compatible with the current Python binding (it runs the same test suite,
  unmodified)

* easier to install, since the stack is much smaller, and there are 
  no issues with the overrides directory

* faster, since we implement Buffer and save some copies

* faster, since it is "thinner". The ffi Ruby binding is about twice
  as fast as the gobject-introspection one, when running the test suite

* portable across CPython, PyPy and others

* more simply portable to Windows 

* easy to package for pip

Notes
-----

Local user install::

	$ pip install --user -e .
	$ pip3 install --user -e .
	$ pypy -m pip --user -e .

Run all tests::

	$ tox 

Run test suite::

	$ tox test

Run a specific test::

	$ tox -e py27 -- pyvips/tests/test_conversion.py:TestConversion.test_composite

Stylecheck::

        $ tox qa

Generate HTML docs in ``doc/build/html``::

        $ cd doc; sphinx-build -bhtml . build/html

Regenerate autodocs::

        $ cd doc; \
          python -c "import pyvips; pyvips.Operation.generate_sphinx_all()" > x 

And copy-paste ``x`` into the obvious place in ``doc/vimage.rst``.

Update version number::

        $ vi pyvips/version.py
        $ vi doc/conf.py

Update pypi package::

        $ python setup.py bdist_wheel
        $ twine upload dist/*


