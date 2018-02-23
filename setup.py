"""a binding for the libvips image processing library

See:
https://github.com/jcupitt/pyvips
"""

# flake8: noqa

import sys
from codecs import open
from os import path

from setuptools import setup, find_packages

# normally we attempt to setup in API mode (with a C extension), but when making
# a wheel, we want to pretend to be a pure Python wheel ... use --abi to go into
# pure Python mode
ABI_mode = False
if "--abi" in sys.argv:
    ABI_mode = True
    sys.argv.remove("--abi")

here = path.abspath(path.dirname(__file__))

info = {}
with open(path.join(here, 'pyvips', 'version.py'), encoding='utf-8') as f:
    exec(f.read(), info)

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
pyvips_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Multimedia :: Graphics :: Graphics Conversion',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Programming Language :: Python :: Implementation :: CPython',
]

setup_deps = [
    'cffi>=1.0.0',
    'pytest-runner',
]

install_deps = [
    'cffi>=1.0.0',
]

test_deps = [
    'cffi>=1.0.0',
    'pytest',
    'pytest-catchlog',
    'pytest-flake8',
]

extras = {
    'test': test_deps,
    'doc': ['sphinx', 'sphinx_rtd_theme'],
}

pyvips_packages = find_packages(exclude=['docs', 'tests', 'examples'])

sys.path.append(path.join(here, 'pyvips'))

def API_setup():
    setup(
        name='pyvips',
        version=info['__version__'],
        description='binding for the libvips image processing library, API mode',
        long_description=long_description,
        url='https://github.com/jcupitt/pyvips',
        author='John Cupitt',
        author_email='jcupitt@gmail.com',
        license='MIT',
        classifiers=pyvips_classifiers,
        keywords='image processing',

        packages=pyvips_packages,
        setup_requires=setup_deps + ['pkgconfig'],
        cffi_modules=['pyvips/pyvips_build.py:ffibuilder'],
        install_requires=install_deps + ['pkgconfig'],
        tests_require=test_deps,
        extras_require=extras,

        # we will try to compile as part of install, so we can't run in a zip
        zip_safe=False,
    )

def ABI_setup():
    setup(
        name='pyvips',
        version=info['__version__'],
        description='binding for the libvips image processing library, ABI mode',
        long_description=long_description,
        url='https://github.com/jcupitt/pyvips',
        author='John Cupitt',
        author_email='jcupitt@gmail.com',
        license='MIT',
        classifiers=pyvips_classifiers,
        keywords='image processing',

        packages=pyvips_packages,
        setup_requires=setup_deps,
        install_requires=install_deps,
        tests_require=test_deps,
        extras_require=extras,
    )


# we try to install twice: first, in API mode (which will try to build some C
# against the libvips headers), then if that fails, in ABI mode, which just
# needs the shared library

if not ABI_mode:
    try:
        API_setup()
    except Exception:
        ABI_mode = True

if ABI_mode:
    ABI_setup()
