"""a binding for the libvips image processing library

See:
https://github.com/jcupitt/pyvips
"""

from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# py3 does not have execfile()
# see https://stackoverflow.com/a/41658338/894763
def _my_execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)

# pull in __version__ -- we can't import it, since that would execute
# __init__.py, which won't run because we haven't installed cffi yet
_my_execfile(path.join(here, 'pyvips', 'version.py'), globals())

test_deps = [
    'nose',
    'flake8'
]

extras = {
    'test': test_deps,
    'doc': ['sphinx', 'sphinx_rtd_theme']
}

setup(
    name='pyvips',
    version=__version__,
    description='binding for the libvips image processing library',
    long_description=long_description,
    url='https://github.com/jcupitt/pyvips',
    author='John Cupitt',
    author_email='jcupitt@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
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
    ],

    keywords='image processing',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples',
                                    'test_images']),

    install_requires=['cffi'],

    tests_require=test_deps,
    extras_require=extras,

)
