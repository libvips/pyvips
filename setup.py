import sys

from os import path
from setuptools import setup

base_dir = path.dirname(__file__)
src_dir = path.join(base_dir, 'pyvips')

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the pyvips/ directory to the sys.path.
sys.path.insert(0, src_dir)

# Try to install in API mode first, then if that fails, fall back to ABI

# API mode requires a working C compiler plus all the libvips headers whereas
# ABI only needs the libvips shared library to be on the system

try:
    setup(cffi_modules=['pyvips/pyvips_build.py:ffibuilder'])
except Exception as e:
    print(f'Falling back to ABI mode. Details: {e}')
    setup()
