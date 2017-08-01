"""a binding for the libvips image processing library

See:
https://github.com/jcupitt/pyvips
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pyvips',
    version = '2.0.0.dev1',
    description = 'binding for the libvips image processing library',
    long_description = long_description,
    url = 'https://github.com/jcupitt/pyvips',
    author = 'John Cupitt',
    author_email = 'jcupitt@gmail.com',
    license = 'MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
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
    ],

    keywords = 'image processing',
    packages = find_packages(exclude = ['contrib', 'docs', 'tests']),

    install_requires=['cffi'],

    extras_require={
        'test': ['nose'],
    },
    test_suite = 'nose.collector',

)
