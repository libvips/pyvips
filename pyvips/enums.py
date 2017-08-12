"""
:mod:`enums` -- The libvips enums
=================================

.. module:: enums
    :synopsis: The various libvips enums
.. moduleauthor:: John Cupitt <jcupitt@gmail.com>
.. moduleauthor:: Kleis Auke Wolthuizen <x@y.z>

This module contains the various libvips enums as Python classes.

Enums values are represented in pyvips as strings. These classes contain the 
valid strings for each enum. 

"""

from __future__ import division

import logging

logger = logging.getLogger(__name__)


class BandFormat(object):
    """The format of image bands.

    The format used for each band element. Each corresponds to a native C type
    for the current machine.

    ``uchar``
        unsigned char format
    ``char``
        char format
    ``ushort``
        unsigned short format
    ``short``
        short format
    ``uint``
        unsigned int format
    ``int``
        int format
    ``float``
        float format
    ``complex``
        complex (two floats) format
    ``double``
        double float format
    ``dpcomplex``
        double complex (two double) format
    """
    UCHAR = 'uchar'
    CHAR = 'char'
    USHORT = 'ushort'
    SHORT = 'short'
    UINT = 'uint'
    INT = 'int'
    FLOAT = 'float'
    COMPLEX = 'complex'
    DOUBLE = 'double'
    DPCOMPLEX = 'dpcomplex'


class Access(object):
    """The type of access an operation has to supply. 

    ``random``
        requests can come in any order. 
    ``sequential``
        means requests will be top-to-bottom, but with some
        amount of buffering behind the read point for small non-local
        accesses. 
    """
    RANDOM = 'random'
    SEQUENTIAL = 'sequential'


class Interpretation(object):
    MULTIBAND = 'multiband'
    B_W = 'b-w'
    HISTOGRAM = 'histogram'
    XYZ = 'xyz'
    LAB = 'lab'
    CMYK = 'cmyk'
    LABQ = 'labq'
    RGB = 'rgb'
    CMC = 'cmc'
    LCH = 'lch'
    LABS = 'labs'
    SRGB = 'srgb'
    YXY = 'yxy'
    FOURIER = 'fourier'
    RGB16 = 'rgb16'
    GREY16 = 'grey16'
    MATRIX = 'matrix'
    SCRGB = 'scrgb'
    HSV = 'hsv'


class Angle(object):
    D0 = 'd0'
    D90 = 'd90'
    D180 = 'd180'
    D270 = 'd270'


class Angle45(object):
    D0 = 'd0'
    D45 = 'd45'
    D90 = 'd90'
    D135 = 'd135'
    D180 = 'd180'
    D225 = 'd225'
    D270 = 'd270'
    D315 = 'd315'


class Intent(object):
    PERCEPTUAL = 'perceptual'
    RELATIVE = 'relative'
    SATURATION = 'saturation'
    ABSOLUTE = 'absolute'


class Extend(object):
    BLACK = 'black'
    COPY = 'copy'
    REPEAT = 'repeat'
    MIRROR = 'mirror'
    WHITE = 'white'
    BACKGROUND = 'background'


class Precision(object):
    INTEGER = 'integer'
    FLOAT = 'float'
    APPROXIMATE = 'approximate'


class Coding(object):
    NONE = 'none'
    LABQ = 'labq'
    RAD = 'rad'


class Direction(object):
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Align(object):
    LOW = 'low'
    CENTRE = 'centre'
    HIGH = 'high'


class Combine(object):
    MAX = 'max'
    SUM = 'sum'


class PCS(object):
    LAB = 'lab'
    XYZ = 'xyz'
