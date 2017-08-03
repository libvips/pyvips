# enums

from __future__ import division

import logging

logger = logging.getLogger(__name__)

# you can supply enum values as strings or ints ... these classes give the ints
# for each string, so pyvips.BandFormat.SHORT is equivalent to 'short'

class BandFormat(object):
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

