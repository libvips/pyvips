"""a binding for the libvips image processing library

See:
https://github.com/jcupitt/pyvips
"""

from __future__ import print_function
from os import path

from setuptools import setup

# so that pyvips_build.py can find decls.py
import sys
here = path.abspath(path.dirname(__file__))
sys.path.append(path.join(here, 'pyvips'))

try:
    # first try to setup using ffibuilder ... this can fail if vips.pc is not
    # found, or if there is no C compiler, for example
    setup(cffi_modules=['pyvips/pyvips_build.py:ffibuilder'])
except: 
    print('unable to build C extension, falling back to ABI mode')
    pass

# setup without install-time build of the generated code
setup()

