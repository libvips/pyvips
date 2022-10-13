README
======

.. image:: https://github.com/libvips/pyvips/workflows/CI/badge.svg
    :alt: Build Status
    :target: https://github.com/libvips/pyvips/actions

PyPI package:

https://pypi.python.org/pypi/pyvips

conda package:

https://anaconda.org/conda-forge/pyvips

We have formatted docs online here:

https://libvips.github.io/pyvips/

This module wraps the libvips image processing library:

https://libvips.github.io/libvips/

The libvips docs are also very useful:

https://libvips.github.io/libvips/API/current/

If you have the development headers for libvips installed and have a working C
compiler, this module will use cffi API mode to try to build a libvips 
binary extension for your Python. 

If it is unable to build a binary extension, it will use cffi ABI mode
instead and only needs the libvips shared library. This takes longer to
start up and is typically ~20% slower in execution.  You can find out how
pyvips installed with ``pip show pyvips``.

This binding passes the vips test suite cleanly and with no leaks under
python2.7 - python3.10, pypy and pypy3 on Windows, macOS and Linux. 

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

conda install
-------------

The conda package includes a matching libvips binary, so just enter:

.. code-block:: shell

    $ conda install --channel conda-forge pyvips

Non-conda install
-----------------

First, you need the libvips shared library on your library search path,
version 8.2 or later, though at least version 8.9 is required for all features
to work.  On Linux and macOS, you can just install via your package manager;
on Windows you can download a pre-compiled binary from the libvips website.

https://libvips.github.io/libvips/install.html

Next, install this package, perhaps:

.. code-block:: shell

    $ pip install --user pyvips

On Windows, you'll need a 64-bit Python. The official one works well. 
You will also need to add ``vips-dev-x.y\bin`` to your ``PATH`` so
that pyvips can find all the DLLs it needs. You can either do this in the
**Advanced System Settings** control panel, or you can just change
``PATH`` in your Python program.

If you set the ``PATH`` environment variable in the control panel, you can
use the ``vips`` command-line tools, which I find useful. However, this will
add a lot of extra DLLs to your search path and they might conflict with
other programs, so it's usually safer just to set ``PATH`` in your program.

To set ``PATH`` from within Python, you need something like this at the
start:

.. code-block:: python

    import os
    vipsbin = r'c:\vips-dev-8.13\bin'
    os.environ['PATH'] = vipsbin + ';' + os.environ['PATH']

For Python 3.8 and later, you need:

.. code-block:: python

    import os
    vipsbin = r'c:\vips-dev-8.13\bin'
    add_dll_dir = getattr(os, 'add_dll_directory', None)
    if callable(add_dll_dir):
        add_dll_dir(vipsbin)
    else:
        os.environ['PATH'] = os.pathsep.join((vipsbin, os.environ['PATH']))

Now when you import pyvips, it should be able to find the DLLs.

Example
-------

This sample program loads a JPG image, doubles the value of every green pixel,
sharpens, and then writes the image back to the filesystem again:

.. code-block:: python

    import pyvips

    image = pyvips.Image.new_from_file('some-image.jpg', access='sequential')
    image *= [1, 2, 1]
    mask = pyvips.Image.new_from_array([
        [-1, -1, -1],
        [-1, 16, -1],
        [-1, -1, -1],
    ], scale=8)
    image = image.conv(mask, precision='integer')
    image.write_to_file('x.jpg')


Notes
-----

Local user install:

.. code-block:: shell

    $ pip3 install -e .
    $ pypy -m pip --user -e .

Run all tests:

.. code-block:: shell

    $ tox 

Run test suite:

.. code-block:: shell

    $ pytest

Run a specific test:

.. code-block:: shell

    $ pytest tests/test_saveload.py

Run perf tests:

.. code-block:: shell

   $ cd tests/perf
   $ ./run.sh

Stylecheck:

.. code-block:: shell

    $ flake8

Generate HTML docs in ``doc/build/html``:

.. code-block:: shell

    $ cd doc; sphinx-build -bhtml . build/html

Regenerate enums:

Make sure you have installed a libvips with all optional packages enabled,
then

.. code-block:: shell

    $ cd examples; \
      ./gen-enums.py ~/GIT/libvips/libvips/Vips-8.0.gir > enums.py

Then check and move `enums.py` into `pyvips/`.

Regenerate autodocs:

Make sure you have installed a libvips with all optional packages enabled,
then

.. code-block:: shell

    $ cd doc; \
      python3 -c "import pyvips; pyvips.Operation.generate_sphinx_all()" > x 

And copy-paste ``x`` into the obvious place in ``doc/vimage.rst``. 

Update version number:

.. code-block:: shell

    $ vi pyvips/version.py
    $ vi doc/conf.py

Update pypi package:

.. code-block:: shell

    $ python3 setup.py sdist
    $ twine upload dist/*
    $ git tag -a v2.2.0 -m "as uploaded to pypi"
    $ git push origin v2.2.0

