README
======

Status
------

This binding passes the vips test suite cleanly and with no leaks under python2
and python3, on Windows and Linux. The docs still need updating and it could 
use a little polish.

Install
-------

You need the libvips shared library on your library search path, version 8.2 or
later. On linux, you can install via your package manager, on Windows you
can download a pre-compiled binary from the libvips website:

https://jcupitt.github.io/libvips/

Then just install this package, perhaps::

	$ pip install --user -e .

Example
-------

Sample program to load a JPG image, double the value of every green pixel,
sharpen, and write back to the filesystem again::

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

This is supposed to be an experiment with making a libvips binding using cffi.

http://cffi.readthedocs.io/en/latest/ref.html

The Python binding included in libvips works, but porting and installation
are more difficult than they should be. 

We've made a libvips binding for luajit:

https://github.com/jcupitt/lua-vips

Python's CFFI is based on luajit's ffi interface, so perhaps we can steal some
of it. 

The hope is that a new Python binding on top of cffi would be:

* compatible with the current Python binding (it should run the same test suite,
  unmodified)

* easier to install, since the stack would be much smaller, and there would be
  no issues with the overrides directory

* faster, since we could implement Buffer and save some copies

* faster, since we could make it "thinner". The ffi Ruby binding is about twice
  as fast as the gobject-introspection one, when running the test suite

* portable across CPython, PyPy and others

* more simply portable to Windows 

* easier to package for pip

Notes
-----

Local user install::

	$ pip install --user -e .
	$ pip3 install --user -e .

Run test suite::

	$ nosetests --logging-level=WARNING
	$ python3 -m nose --logging-level=WARNING

Stylecheck::

        $ flake8

Generate HTML docs in ``doc/build/html``::

        $ cd doc; sphinx-build -bhtml . build/html

