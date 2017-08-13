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
    """How the values in an image should be interpreted. 
    
    For example, a three-band float image of type :lab should have its 
    pixels interpreted as coordinates in CIE Lab space.

    ``multiband`` 
        generic many-band image
    ``b_w`` 
        some kind of single-band image
    ``histogram`` 
        a 1D image, eg. histogram or lookup table
    ``fourier`` 
        image is in fourier space
    ``xyz`` 
        the first three bands are CIE XYZ 
    ``lab`` 
        pixels are in CIE Lab space
    ``cmyk`` 
        the first four bands are in CMYK space
    ``labq`` 
        implies #VIPS_CODING_LABQ
    ``rgb`` 
        generic RGB space
    ``cmc`` 
        a uniform colourspace based on CMC(1:1)
    ``lch`` 
        pixels are in CIE LCh space
    ``labs`` 
        CIE LAB coded as three signed 16-bit values
    ``srgb`` 
        pixels are sRGB
    ``hsv`` 
        pixels are HSV
    ``scrgb`` 
        pixels are scRGB
    ``yxy`` 
        pixels are CIE Yxy
    ``rgb16`` 
        generic 16-bit RGB
    ``grey16`` 
        generic 16-bit mono
    ``matrix`` 
        a matrix

    """

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
    """Various fixed 90 degree rotation angles. 
    
    See for example :meth:`.rot`.

    ``d0`` 
        no rotate
    ``d90`` 
        90 degrees clockwise
    ``d180`` 
        180 degrees 
    ``d270`` 
        90 degrees anti-clockwise

    """

    D0 = 'd0'
    D90 = 'd90'
    D180 = 'd180'
    D270 = 'd270'


class Angle45(object):
    """Various fixed 45 degree rotation angles. 
    
    See for example :meth:`.rot45`.

    ``d0`` 
        no rotate
    ``d45`` 
        45 degrees clockwise 
    ``d90`` 
        90 degrees clockwise
    ``d135`` 
        135 degrees clockwise
    ``d180`` 
        180 degrees 
    ``d225`` 
        135 degrees anti-clockwise
    ``d270`` 
        90 degrees anti-clockwise
    ``d315`` 
        45 degrees anti-clockwise

    """

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
    """How to extend image edges.

    When the edges of an image are extended, you can specify
    how you want the extension done. 
    See :meth:`.embed`, :meth:`.conv`, :meth:`.affine` and 
    so on.

    ``black`` 
        new pixels are black, ie. all bits are zero. 
    ``copy`` 
        each new pixel takes the value of the nearest edge pixel
    ``repeat`` 
        the image is tiled to fill the new area
    ``mirror`` 
        the image is reflected and tiled to reduce hash edges
    ``white`` 
        new pixels are white, ie. all bits are set
    ``background`` 
        colour set from the @background property

    """

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
    """How pixels are coded. 

    Normally, pixels are uncoded and can be manipulated as you would expect.
    However some file formats code pixels for compression, and sometimes it's
    useful to be able to manipulate images in the coded format.

    ``none`` 
        pixels are not coded
    ``labq`` 
        pixels encode 3 float CIELAB values as 4 uchar
    ``rad`` 
        pixels encode 3 float RGB as 4 uchar (Radiance coding)

    """

    NONE = 'none'
    LABQ = 'labq'
    RAD = 'rad'


class Direction(object):
    """A direction.

    Operations like :meth:`.flip` need to be told whether to flip 
    left-right or top-bottom. 

    ``horizontal`` 
        left-right 
    ``vertical`` 
        top-bottom

    """

    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Align(object):
    """Various types of alignment. 
    
    See :meth:`.join`, for example.

    ``low`` 
        Align on the low coordinate edge
    ``centre`` 
        Align on the centre
    ``high`` 
        Align on the high coordinate edge

    """

    LOW = 'low'
    CENTRE = 'centre'
    HIGH = 'high'


class Combine(object):
    MAX = 'max'
    SUM = 'sum'


class PCS(object):
    LAB = 'lab'
    XYZ = 'xyz'
