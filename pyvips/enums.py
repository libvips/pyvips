from __future__ import division


class BandFormat(object):
    """The format of image bands.

    The format used for each band element. Each corresponds to a native C type
    for the current machine.

    Attributes:
        UCHAR (str): unsigned char format
        CHAR (str): char format
        USHORT (str): unsigned short format
        SHORT (str): short format
        UINT (str): unsigned int format
        INT (str): int format
        FLOAT (str): float format
        COMPLEX (str): complex (two floats) format
        DOUBLE (str): double float format
        DPCOMPLEX (str): double complex (two double) format

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

    Attributes:
        RANDOM (str): Requests can come in any order.
        SEQUENTIAL (str): Means requests will be top-to-bottom, but with some
            amount of buffering behind the read point for small non-local
            accesses.

    """

    RANDOM = 'random'
    SEQUENTIAL = 'sequential'


class Interpretation(object):
    """How the values in an image should be interpreted.

    For example, a three-band float image of type LAB should have its
    pixels interpreted as coordinates in CIE Lab space.

    Attributes:
        MULTIBAND (str): generic many-band image
        B_W (str): some kind of single-band image
        HISTOGRAM (str): a 1D image, eg. histogram or lookup table
        FOURIER (str): image is in fourier space
        XYZ (str): the first three bands are CIE XYZ
        LAB (str): pixels are in CIE Lab space
        CMYK (str): the first four bands are in CMYK space
        LABQ (str): implies #VIPS_CODING_LABQ
        RGB (str): generic RGB space
        CMC (str): a uniform colourspace based on CMC(1:1)
        LCH (str): pixels are in CIE LCh space
        LABS (str): CIE LAB coded as three signed 16-bit values
        SRGB (str): pixels are sRGB
        HSV (str): pixels are HSV
        SCRGB (str): pixels are scRGB
        YXY (str): pixels are CIE Yxy
        RGB16 (str): generic 16-bit RGB
        GREY16 (str): generic 16-bit mono
        MATRIX (str): a matrix

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

    Attributes:
        D0 (str): no rotate
        D90 (str): 90 degrees clockwise
        D180 (str): 180 degrees
        D270 (str): 90 degrees anti-clockwise

    """

    D0 = 'd0'
    D90 = 'd90'
    D180 = 'd180'
    D270 = 'd270'


class Angle45(object):
    """Various fixed 45 degree rotation angles.

    See for example :meth:`.rot45`.

    Attributes:
        D0 (str): no rotate
        D45 (str): 45 degrees clockwise
        D90 (str): 90 degrees clockwise
        D135 (str): 135 degrees clockwise
        D180 (str): 180 degrees
        D225 (str): 135 degrees anti-clockwise
        D270 (str): 90 degrees anti-clockwise
        D315 (str): 45 degrees anti-clockwise

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
    """The rendering intent.

    See :meth:`.icc_transform`.

    Attributes:
        PERCEPTUAL (str):
        RELATIVE (str):
        SATURATION (str):
        ABSOLUTE (str):

    """

    PERCEPTUAL = 'perceptual'
    RELATIVE = 'relative'
    SATURATION = 'saturation'
    ABSOLUTE = 'absolute'


class Extend(object):
    """How to extend image edges.

    When the edges of an image are extended, you can specify how you want
    the extension done.  See :meth:`.embed`, :meth:`.conv`, :meth:`.affine`
    and so on.

    Attributes:
        BLACK (str): new pixels are black, ie. all bits are zero.
        COPY (str): each new pixel takes the value of the nearest edge pixel
        REPEAT (str): the image is tiled to fill the new area
        MIRROR (str): the image is reflected and tiled to reduce hash edges
        WHITE (str): new pixels are white, ie. all bits are set
        BACKGROUND (str): colour set from the @background property

    """

    BLACK = 'black'
    COPY = 'copy'
    REPEAT = 'repeat'
    MIRROR = 'mirror'
    WHITE = 'white'
    BACKGROUND = 'background'


class Precision(object):
    """Computation precision.

    See for example :meth:`.conv`.

    Attributes:
        INTEGER (str): Integer.
        FLOAT (str): Floating point.
        APPROXIMATE (str): Compute approximate result.

    """

    INTEGER = 'integer'
    FLOAT = 'float'
    APPROXIMATE = 'approximate'


class Coding(object):
    """How pixels are coded.

    Normally, pixels are uncoded and can be manipulated as you would expect.
    However some file formats code pixels for compression, and sometimes it's
    useful to be able to manipulate images in the coded format.

    Attributes:
        NONE (str): pixels are not coded
        LABQ (str): pixels encode 3 float CIELAB values as 4 uchar
        RAD (str): pixels encode 3 float RGB as 4 uchar (Radiance coding)

    """

    NONE = 'none'
    LABQ = 'labq'
    RAD = 'rad'


class Direction(object):
    """A direction.

    Operations like :meth:`.flip` need to be told whether to flip
    left-right or top-bottom.

    Attributes:
        HORIZONTAL (str): left-right
        VERTICAL (str): top-bottom

    """

    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Align(object):
    """Various types of alignment.

    See :meth:`.join`, for example.

    Attributes:
        LOW (str): Align on the low coordinate edge
        CENTRE (str): Align on the centre
        HIGH (str): Align on the high coordinate edge

    """

    LOW = 'low'
    CENTRE = 'centre'
    HIGH = 'high'


class Combine(object):
    """How to combine passes.

    See for example :meth:`.compass`.

    Attributes:
        MAX (str): Take the maximum of all values.
        SUM (str): Take the sum of all values.

    """

    MAX = 'max'
    SUM = 'sum'


class PCS(object):
    """Set Perofile Connection Space.

    See for example :meth:`.icc_import`.

    Attributes:
        LAB (str): CIE Lab space.
        XYZ (str): CIE XYZ space.

    """

    LAB = 'lab'
    XYZ = 'xyz'
