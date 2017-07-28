# pyvips --- experimental CFFI binding for libvips

This is supposed to be an experiment with making a libvips binding using cffi.

http://cffi.readthedocs.io/en/latest/ref.html

The python binding included in libvips works OK, but porting and installation
are more difficult than they should be. 

We've made a libvips binding in luajit:

https://github.com/jcupitt/lua-vips

Python's CFFI is based on luajit's ffi interface, so perhaps we can steal some
of it. 

The hope here is that rebuilding the python binding on top of cffi would:

* compatible with the current Python binding (it should run the same test suite,
  unmodified)

* easier to install, since the stack would be much smaller, and there would be
  no issues with the overrides directory

* faster, since we could implement Buffer and save some copies

* faster, since we could make it "thinner". The ffi Ruby binding is about twice
  as fast as the gobject-itrospection one, when running the test suite

* portable across CPython, PyPy and others

* more simply portable to Windows 

* easier to package for pip

