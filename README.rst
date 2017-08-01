========
 pyvips 
========
--------------------------------------------
pyvips experimental CFFI binding for libvips
--------------------------------------------

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

	$ nosetests |& more
	$ nosetests --logging-level=WARNING

Converting old code
-------------------

Replace the lines::

	import gi
	gi.require_version('Vips', '8.0')
	from gi.repository import Vips 

with::

	import pyvips
	Vips = pyvips
