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

https://www.libvips.org/

The libvips docs are also very useful:

https://www.libvips.org/API/current/

If you have the development headers for libvips installed and have a working C
compiler, this module will use cffi API mode to try to build a libvips
binary extension for your Python.

If it is unable to build a binary extension, it will use cffi ABI mode
instead and only needs the libvips shared library. This takes longer to
start up and is typically ~20% slower in execution. You can find out if
API mode is being used with:

.. code-block:: python

    import pyvips

    print(pyvips.API_mode)

This binding passes the vips test suite cleanly and with no leaks under
python3 and pypy3 on Windows, macOS and Linux.

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

https://www.libvips.org/API/current/How-it-opens-files.html

Binary installation
-------------------

The quickest way to start with pyvips is by installing the binary package
with:

.. code-block:: shell

    $ pip install "pyvips[binary]"

This installs a self-contained package with the most commonly needed
libraries. If your platform is unsupported or the pre-built binary is
unsuitable, you can install libvips globally instead.

Local installation
------------------

You need the libvips shared library on your library search path, version 8.2
or later, though at least version 8.9 is required for all features to work.
See:

https://www.libvips.org/install.html

Linux
^^^^^

Perhaps:

.. code-block:: shell

    $ sudo apt install libvips-dev --no-install-recommends
    $ pip install pyvips

With python 3.11 and later, you will need to create a venv first and add
`path/to/venv` to your `PATH`. Something like:

.. code-block:: shell

    $ python3 -m venv ~/.local
    $ pip install pyvips

macOS
^^^^^

With Homebrew:

.. code-block:: shell

    $ brew install vips python pkg-config
    $ pip3 install pyvips

Windows
^^^^^^^

On Windows, you can download a pre-compiled binary from the libvips website.

https://www.libvips.org/install.html

You'll need a 64-bit Python. The official one works well.

You can add ``vips-dev-x.y\bin`` to your ``PATH``, but this will add a lot of
extra DLLs to your search path and they might conflict with other programs,
so it's usually safer to set ``PATH`` in your program.

To set ``PATH`` from within Python, you need something like this at the
start of your program:

.. code-block:: python

    import os
    vipsbin = r'c:\vips-dev-8.16\bin'
    os.environ['PATH'] = vipsbin + ';' + os.environ['PATH']

For Python 3.8 and later, you need:

.. code-block:: python

    import os
    vipsbin = r'c:\vips-dev-8.16\bin'
    add_dll_dir = getattr(os, 'add_dll_directory', None)
    if callable(add_dll_dir):
        add_dll_dir(vipsbin)
    else:
        os.environ['PATH'] = os.pathsep.join((vipsbin, os.environ['PATH']))

Now when you import pyvips, it should be able to find the DLLs.

Conda
^^^^^

The Conda package includes a matching libvips binary, so just enter:

.. code-block:: shell

    $ conda install --channel conda-forge pyvips

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
      ./gen-enums.py ~/GIT/libvips/build/libvips/Vips-8.0.gir > enums.py

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

    $ python3 -m build --sdist
    $ twine upload --repository pyvips dist/*
    $ git tag -a v2.2.0 -m "as uploaded to pypi"
    $ git push origin v2.2.0
