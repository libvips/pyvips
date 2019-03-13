README
======

.. image:: https://travis-ci.org/libvips/pyvips.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/libvips/pyvips

PyPI package:

https://pypi.python.org/pypi/pyvips

This module wraps the libvips image processing library. 

https://libvips.github.io/libvips/

If you have the development headers for libvips installed and have a working C
compiler, this module will use cffi API mode to try to build a libvips 
binary extension for your Python. 

If it is unable to build a binary extension, it will use cffi ABI mode
instead and only needs the libvips shared library. This takes longer to
start up and is typically ~20% slower in execution.  You can find out how
pyvips installed with ``pip show pyvips``.

This binding passes the vips test suite cleanly and with no leaks under
python2.7 - python3.6, pypy and pypy3 on Windows, macOS and Linux. 

We have formatted docs online here:

https://libvips.github.io/pyvips/

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

https://github.com/libvips/libvips/wiki/Speed-and-memory-use

Loads a large tiff image, shrinks by 10%, sharpens, and saves again. On this
test ``pyvips`` is typically 3x faster than ImageMagick and needs 5x less
memory. 

There's a handy chapter in the docs explaining how libvips opens files,
which gives some more background.

http://libvips.github.io/libvips/API/current/How-it-opens-files.md.html

Install libvips
---------------

You need the libvips shared library on your library search path, version 8.2 or
later. On Linux and macOS, you can just install via your package manager; on 
Windows you can download a pre-compiled binary from the libvips website.

https://libvips.github.io/libvips/install.html

Install pyvips
--------------

Next, install this package, perhaps::

    $ pip install --user pyvips

On Windows, you'll need a 64-bit Python. The official one works well. Anaconda
probably won't work without some effort -- they have their own packaging
system.

Extra notes for Windows
-----------------------

On Windows, you will need to add `vips-dev-x.y\bin` to your `PATH` so
that pyvips can find all the DLLs it needs. You can either do this in the
**Advanced System Settings** control panel, or you can just change
`PATH` for your pyvips program.

If you set the PATH environment variable in the control panel, you can use
the `vips` command-line tools, which I find useful. However, this will add
a lot of extra DLLs to your search path and they might conflict with other
programs, so it's usually safer just to set `PATH` in your program.

To set `PATH` from within Python, you need something like this at the start of
your program::

    import os
    vipshome = 'c:\\vips-dev-8.7\\bin'
    os.environ['PATH'] = vipshome + ';' + os.environ['PATH']

Now when you import pyvips, it should be able to find the DLLs.

Test your install
-----------------

Try this test program::

    import logging; logging.basicConfig(level = logging.DEBUG)
    import pyvips

If pyvips was able to build and use a binary module on your computer (API
mode) you should see::

    $ ./pyv.py 
    DEBUG:pyvips:Loaded binary module _libvips
    DEBUG:pyvips:Inited libvips

If the build failed (fallback to ABI mode), or there was a header or version
mismatch, you might see::

    $ ./pyv.py 
    DEBUG:pyvips:Loaded binary module _libvips
    DEBUG:pyvips:Binary module load failed: not all arguments converted during string formatting
    DEBUG:pyvips:Falling back to ABI mode
    DEBUG:pyvips:Loaded lib <cffi.api.FFILibrary_libvips.so.42 object at 0x7f29fa015190>
    DEBUG:pyvips:Loaded lib <cffi.api.FFILibrary_libgobject-2.0.so.0 object at 0x7f29fa015110>
    DEBUG:pyvips:Inited libvips

pyvips will work fine in this fallback mode, it's just a bit slower. 

If API mode stops working, you can fix it by reinstalling pyvips. You should
make sure pip is not reusing a cached wheel, e.g. by using ``pip install
--no-cache-dir pyvips``.

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

    $ pytest tests/test_conversion.py

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

    $ python setup.py sdist
    $ twine upload dist/*

