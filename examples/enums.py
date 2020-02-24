class BandFormat(object):
    """BandFormat.
    
    The format used for each band element.

Each corresponds to a native C type for the current machine. For example,
#VIPS_FORMAT_USHORT is <type>unsigned short</type>.
    
    NOTSET - invalid setting
    UCHAR - unsigned char format
    CHAR - char format
    USHORT - unsigned short format
    SHORT - short format
    UINT - unsigned int format
    INT - int format
    FLOAT - float format
    COMPLEX - complex (two floats) format
    DOUBLE - double float format
    DPCOMPLEX - double complex (two double) format
    """
    
    NOTSET = 'notset'
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


class BlendMode(object):
    """BlendMode.
    
    The various Porter-Duff and PDF blend modes. See vips_composite(),
for example.

The Cairo docs have a nice explanation of all the blend modes:

https://www.cairographics.org/operators

The non-separable modes are not implemented.
    
    CLEAR - where the second object is drawn, the first is removed
    SOURCE - the second object is drawn as if nothing were below
    OVER - the image shows what you would expect if you held two semi-transparent slides on top of each other
    IN - the first object is removed completely, the second is only drawn where the first was
    OUT - the second is drawn only where the first isn't
    ATOP - this leaves the first object mostly intact, but mixes both objects in the overlapping area
    DEST - leaves the first object untouched, the second is discarded completely
    DEST_OVER - like OVER, but swaps the arguments
    DEST_IN - like IN, but swaps the arguments
    DEST_OUT - like OUT, but swaps the arguments
    DEST_ATOP - like ATOP, but swaps the arguments
    XOR - something like a difference operator
    ADD - a bit like adding the two images
    SATURATE - a bit like the darker of the two
    MULTIPLY - at least as dark as the darker of the two inputs
    SCREEN - at least as light as the lighter of the inputs
    OVERLAY - multiplies or screens colors, depending on the lightness
    DARKEN - the darker of each component
    LIGHTEN - the lighter of each component
    COLOUR_DODGE - brighten first by a factor second
    COLOUR_BURN - darken first by a factor of second
    HARD_LIGHT - multiply or screen, depending on lightness
    SOFT_LIGHT - darken or lighten, depending on lightness
    DIFFERENCE - difference of the two
    EXCLUSION - somewhat like DIFFERENCE, but lower-contrast
    """
    
    CLEAR = 'clear'
    SOURCE = 'source'
    OVER = 'over'
    IN = 'in'
    OUT = 'out'
    ATOP = 'atop'
    DEST = 'dest'
    DEST_OVER = 'dest-over'
    DEST_IN = 'dest-in'
    DEST_OUT = 'dest-out'
    DEST_ATOP = 'dest-atop'
    XOR = 'xor'
    ADD = 'add'
    SATURATE = 'saturate'
    MULTIPLY = 'multiply'
    SCREEN = 'screen'
    OVERLAY = 'overlay'
    DARKEN = 'darken'
    LIGHTEN = 'lighten'
    COLOUR_DODGE = 'colour-dodge'
    COLOUR_BURN = 'colour-burn'
    HARD_LIGHT = 'hard-light'
    SOFT_LIGHT = 'soft-light'
    DIFFERENCE = 'difference'
    EXCLUSION = 'exclusion'


class Coding(object):
    """Coding.
    
    How pixels are coded.

Normally, pixels are uncoded and can be manipulated as you would expect.
However some file formats code pixels for compression, and sometimes it's
useful to be able to manipulate images in the coded format.

The gaps in the numbering are historical and must be maintained. Allocate
new numbers from the end.
    
    NONE - pixels are not coded
    LABQ - pixels encode 3 float CIELAB values as 4 uchar
    RAD - pixels encode 3 float RGB as 4 uchar (Radiance coding)
    """
    
    ERROR = 'error'
    NONE = 'none'
    LABQ = 'labq'
    RAD = 'rad'


class Interpretation(object):
    """Interpretation.
    
    How the values in an image should be interpreted. For example, a
three-band float image of type #VIPS_INTERPRETATION_LAB should have its
pixels interpreted as coordinates in CIE Lab space.

RGB and sRGB are treated in the same way. Use the colourspace functions if
you want some other behaviour.

The gaps in numbering are historical and must be maintained. Allocate
new numbers from the end.
    
    MULTIBAND - generic many-band image
    B_W - some kind of single-band image
    HISTOGRAM - a 1D image, eg. histogram or lookup table
    XYZ - the first three bands are CIE XYZ
    LAB - pixels are in CIE Lab space
    CMYK - the first four bands are in CMYK space
    LABQ - implies #VIPS_CODING_LABQ
    RGB - generic RGB space
    CMC - a uniform colourspace based on CMC(1:1)
    LCH - pixels are in CIE LCh space
    LABS - CIE LAB coded as three signed 16-bit values
    SRGB - pixels are sRGB
    YXY - pixels are CIE Yxy
    FOURIER - image is in fourier space
    RGB16 - generic 16-bit RGB
    GREY16 - generic 16-bit mono
    MATRIX - a matrix
    SCRGB - pixels are scRGB
    HSV - pixels are HSV
    """
    
    ERROR = 'error'
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


class DemandStyle(object):
    """DemandStyle.
    
    See vips_image_pipelinev(). Operations can hint to the VIPS image IO
system about the kind of demand geometry they prefer.

These demand styles are given below in order of increasing
restrictiveness.  When demanding output from a pipeline,
vips_image_generate()
will use the most restrictive of the styles requested by the operations
in the pipeline.

#VIPS_DEMAND_STYLE_THINSTRIP --- This operation would like to output strips
the width of the image and a few pels high. This is option suitable for
point-to-point operations, such as those in the arithmetic package.

This option is only efficient for cases where each output pel depends
upon the pel in the corresponding position in the input image.

#VIPS_DEMAND_STYLE_FATSTRIP --- This operation would like to output strips
the width of the image and as high as possible. This option is suitable
for area operations which do not violently transform coordinates, such
as vips_conv().

#VIPS_DEMAND_STYLE_SMALLTILE --- This is the most general demand format.
Output is demanded in small (around 100x100 pel) sections. This style works
reasonably efficiently, even for bizzare operations like 45 degree rotate.

#VIPS_DEMAND_STYLE_ANY --- This image is not being demand-read from a disc
file (even indirectly) so any demand style is OK. It's used for things like
vips_black() where the pixels are calculated.

See also: vips_image_pipelinev().
    
    SMALLTILE - demand in small (typically 64x64 pixel) tiles
    FATSTRIP - demand in fat (typically 10 pixel high) strips
    THINSTRIP - demand in thin (typically 1 pixel high) strips
    """
    
    ERROR = 'error'
    SMALLTILE = 'smalltile'
    FATSTRIP = 'fatstrip'
    THINSTRIP = 'thinstrip'


class OperationRelational(object):
    """OperationRelational.
    
    See also: vips_relational().
    
    EQUAL - ==
    NOTEQ - !=
    LESS - <
    LESSEQ - <=
    MORE - >
    MOREEQ - >=
    """
    
    EQUAL = 'equal'
    NOTEQ = 'noteq'
    LESS = 'less'
    LESSEQ = 'lesseq'
    MORE = 'more'
    MOREEQ = 'moreeq'


class OperationBoolean(object):
    """OperationBoolean.
    
    See also: vips_boolean().
    
    AND - &
    OR - |
    EOR - ^
    LSHIFT - >>
    RSHIFT - <<
    """
    
    AND = 'and'
    OR = 'or'
    EOR = 'eor'
    LSHIFT = 'lshift'
    RSHIFT = 'rshift'


class OperationMath2(object):
    """OperationMath2.
    
    See also: vips_math().
    
    POW - pow( left, right )
    WOP - pow( right, left )
    """
    
    POW = 'pow'
    WOP = 'wop'


class OperationComplex2(object):
    """OperationComplex2.
    
    See also: vips_complex2().
    
    CROSS_PHASE - convert to polar coordinates
    """
    
    CROSS_PHASE = 'cross-phase'


class OperationMath(object):
    """OperationMath.
    
    See also: vips_math().
    
    SIN - sin(), angles in degrees
    COS - cos(), angles in degrees
    TAN - tan(), angles in degrees
    ASIN - asin(), angles in degrees
    ACOS - acos(), angles in degrees
    ATAN - atan(), angles in degrees
    LOG - log base e
    LOG10 - log base 10
    EXP - e to the something
    EXP10 - 10 to the something
    """
    
    SIN = 'sin'
    COS = 'cos'
    TAN = 'tan'
    ASIN = 'asin'
    ACOS = 'acos'
    ATAN = 'atan'
    LOG = 'log'
    LOG10 = 'log10'
    EXP = 'exp'
    EXP10 = 'exp10'


class OperationRound(object):
    """OperationRound.
    
    See also: vips_round().
    
    RINT - round to nearest
    CEIL - the smallest integral value not less than
    FLOOR - largest integral value not greater than
    """
    
    RINT = 'rint'
    CEIL = 'ceil'
    FLOOR = 'floor'


class OperationComplex(object):
    """OperationComplex.
    
    See also: vips_complex().
    
    POLAR - convert to polar coordinates
    RECT - convert to rectangular coordinates
    CONJ - complex conjugate
    """
    
    POLAR = 'polar'
    RECT = 'rect'
    CONJ = 'conj'


class OperationComplexget(object):
    """OperationComplexget.
    
    See also: vips_complexget().
    
    REAL - get real component
    IMAG - get imaginary component
    """
    
    REAL = 'real'
    IMAG = 'imag'


class Combine(object):
    """Combine.
    
    How to combine values. See vips_compass(), for example.
    
    MAX - take the maximum of the possible values
    SUM - sum all the values
    MIN - take the minimum value
    """
    
    MAX = 'max'
    SUM = 'sum'
    MIN = 'min'


class Access(object):
    """Access.
    
    The type of access an operation has to supply. See vips_tilecache()
and #VipsForeign.

@VIPS_ACCESS_RANDOM means requests can come in any order.

@VIPS_ACCESS_SEQUENTIAL means requests will be top-to-bottom, but with some
amount of buffering behind the read point for small non-local accesses.
    
    RANDOM - can read anywhere
    SEQUENTIAL - top-to-bottom reading only, but with a small buffer
    """
    
    RANDOM = 'random'
    SEQUENTIAL = 'sequential'
    SEQUENTIAL_UNBUFFERED = 'sequential-unbuffered'


class Extend(object):
    """Extend.
    
    See vips_embed(), vips_conv(), vips_affine() and so on.

When the edges of an image are extended, you can specify
how you want the extension done.

#VIPS_EXTEND_BLACK --- new pixels are black, ie. all bits are zero.

#VIPS_EXTEND_COPY --- each new pixel takes the value of the nearest edge
pixel

#VIPS_EXTEND_REPEAT --- the image is tiled to fill the new area

#VIPS_EXTEND_MIRROR --- the image is reflected and tiled to reduce hash
edges

#VIPS_EXTEND_WHITE --- new pixels are white, ie. all bits are set

#VIPS_EXTEND_BACKGROUND --- colour set from the @background property

We have to specify the exact value of each enum member since we have to
keep these frozen for back compat with vips7.

See also: vips_embed().
    
    BLACK - extend with black (all 0) pixels
    COPY - copy the image edges
    REPEAT - repeat the whole image
    MIRROR - mirror the whole image
    WHITE - extend with white (all bits set) pixels
    BACKGROUND - extend with colour from the @background property
    """
    
    BLACK = 'black'
    COPY = 'copy'
    REPEAT = 'repeat'
    MIRROR = 'mirror'
    WHITE = 'white'
    BACKGROUND = 'background'


class CompassDirection(object):
    """CompassDirection.
    
    A direction on a compass. Used for vips_gravity(), for example.
    
    CENTRE - centre
    NORTH - north
    EAST - east
    SOUTH - south
    WEST - west
    NORTH_EAST - north-east
    SOUTH_EAST - south-east
    SOUTH_WEST - south-west
    NORTH_WEST - north-west
    """
    
    CENTRE = 'centre'
    NORTH = 'north'
    EAST = 'east'
    SOUTH = 'south'
    WEST = 'west'
    NORTH_EAST = 'north-east'
    SOUTH_EAST = 'south-east'
    SOUTH_WEST = 'south-west'
    NORTH_WEST = 'north-west'


class Direction(object):
    """Direction.
    
    See vips_flip(), vips_join() and so on.

Operations like vips_flip() need to be told whether to flip left-right or
top-bottom.

See also: vips_flip(), vips_join().
    
    HORIZONTAL - left-right
    VERTICAL - top-bottom
    """
    
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Align(object):
    """Align.
    
    See vips_join() and so on.

Operations like vips_join() need to be told whether to align images on the
low or high coordinate edge, or centre.

See also: vips_join().
    
    LOW - align low coordinate edge
    CENTRE - align centre
    HIGH - align high coordinate edge
    """
    
    LOW = 'low'
    CENTRE = 'centre'
    HIGH = 'high'


class Interesting(object):
    """Interesting.
    
    Pick the algorithm vips uses to decide image "interestingness". This is used
by vips_smartcrop(), for example, to decide what parts of the image to
keep.

#VIPS_INTERESTING_NONE and #VIPS_INTERESTING_LOW mean the same -- the
crop is positioned at the top or left. #VIPS_INTERESTING_HIGH positions at
the bottom or right.

See also: vips_smartcrop().
    
    NONE - do nothing
    CENTRE - just take the centre
    ENTROPY - use an entropy measure
    ATTENTION - look for features likely to draw human attention
    LOW - position the crop towards the low coordinate
    HIGH - position the crop towards the high coordinate
    """
    
    NONE = 'none'
    CENTRE = 'centre'
    ENTROPY = 'entropy'
    ATTENTION = 'attention'
    LOW = 'low'
    HIGH = 'high'


class Angle(object):
    """Angle.
    
    See vips_rot() and so on.

Fixed rotate angles.

See also: vips_rot().
    
    D0 - no rotate
    D90 - 90 degrees clockwise
    D180 - 180 degree rotate
    D270 - 90 degrees anti-clockwise
    """
    
    D0 = 'd0'
    D90 = 'd90'
    D180 = 'd180'
    D270 = 'd270'


class Angle45(object):
    """Angle45.
    
    See vips_rot45() and so on.

Fixed rotate angles.

See also: vips_rot45().
    
    D0 - no rotate
    D45 - 45 degrees clockwise
    D90 - 90 degrees clockwise
    D135 - 135 degrees clockwise
    D180 - 180 degrees
    D225 - 135 degrees anti-clockwise
    D270 - 90 degrees anti-clockwise
    D315 - 45 degrees anti-clockwise
    """
    
    D0 = 'd0'
    D45 = 'd45'
    D90 = 'd90'
    D135 = 'd135'
    D180 = 'd180'
    D225 = 'd225'
    D270 = 'd270'
    D315 = 'd315'


class Precision(object):
    """Precision.
    
    How accurate an operation should be.
    
    INTEGER - int everywhere
    FLOAT - float everywhere
    APPROXIMATE - approximate integer output
    """
    
    INTEGER = 'integer'
    FLOAT = 'float'
    APPROXIMATE = 'approximate'


class ForeignDzLayout(object):
    """ForeignDzLayout.
    
    What directory layout and metadata standard to use.
    
    DZ - use DeepZoom directory layout
    ZOOMIFY - use Zoomify directory layout
    GOOGLE - use Google maps directory layout
    IIIF - use IIIF directory layout
    """
    
    DZ = 'dz'
    ZOOMIFY = 'zoomify'
    GOOGLE = 'google'
    IIIF = 'iiif'


class ForeignDzDepth(object):
    """ForeignDzDepth.
    
    How many pyramid layers to create.
    
    ONEPIXEL - create layers down to 1x1 pixel
    ONETILE - create layers down to 1x1 tile
    ONE - only create a single layer
    """
    
    ONEPIXEL = 'onepixel'
    ONETILE = 'onetile'
    ONE = 'one'


class ForeignDzContainer(object):
    """ForeignDzContainer.
    
    How many pyramid layers to create.
    
    FS - write tiles to the filesystem
    ZIP - write tiles to a zip file
    SZI - write to a szi file
    """
    
    FS = 'fs'
    ZIP = 'zip'
    SZI = 'szi'


class RegionShrink(object):
    """RegionShrink.
    
    How to calculate the output pixels when shrinking a 2x2 region.
    
    MEAN - use the average
    MEDIAN - use the median
    MODE - use the mode
    MAX - use the maximum
    MIN - use the minimum
    NEAREST - use the top-left pixel
    """
    
    MEAN = 'mean'
    MEDIAN = 'median'
    MODE = 'mode'
    MAX = 'max'
    MIN = 'min'
    NEAREST = 'nearest'


class ForeignJpegSubsample(object):
    """ForeignJpegSubsample.
    
    Set jpeg subsampling mode.
    
    AUTO - default preset
    ON - always perform subsampling
    OFF - never perform subsampling
    """
    
    AUTO = 'auto'
    ON = 'on'
    OFF = 'off'


class ForeignWebpPreset(object):
    """ForeignWebpPreset.
    
    Tune lossy encoder settings for different image types.
    
    DEFAULT - default preset
    PICTURE - digital picture, like portrait, inner shot
    PHOTO - outdoor photograph, with natural lighting
    DRAWING - hand or line drawing, with high-contrast details
    ICON - small-sized colorful images
    TEXT - text-like
    """
    
    DEFAULT = 'default'
    PICTURE = 'picture'
    PHOTO = 'photo'
    DRAWING = 'drawing'
    ICON = 'icon'
    TEXT = 'text'


class ForeignTiffCompression(object):
    """ForeignTiffCompression.
    
    The compression types supported by the tiff writer.

Use @Q to set the jpeg compression level, default 75.

Use @prediction to set the lzw or deflate prediction, default none.

Use @lossless to set WEBP lossless compression.

Use @level to set webp and zstd compression level.
    
    NONE - no compression
    JPEG - jpeg compression
    DEFLATE - deflate (zip) compression
    PACKBITS - packbits compression
    CCITTFAX4 - fax4 compression
    LZW - LZW compression
    WEBP - WEBP compression
    ZSTD - ZSTD compression
    """
    
    NONE = 'none'
    JPEG = 'jpeg'
    DEFLATE = 'deflate'
    PACKBITS = 'packbits'
    CCITTFAX4 = 'ccittfax4'
    LZW = 'lzw'
    WEBP = 'webp'
    ZSTD = 'zstd'


class ForeignTiffPredictor(object):
    """ForeignTiffPredictor.
    
    The predictor can help deflate and lzw compression. The values are fixed by
the tiff library.
    
    NONE - no prediction
    HORIZONTAL - horizontal differencing
    FLOAT - float predictor
    """
    
    NONE = 'none'
    HORIZONTAL = 'horizontal'
    FLOAT = 'float'


class ForeignTiffResunit(object):
    """ForeignTiffResunit.
    
    Use inches or centimeters as the resolution unit for a tiff file.
    
    CM - use centimeters
    INCH - use inches
    """
    
    CM = 'cm'
    INCH = 'inch'


class ForeignHeifCompression(object):
    """ForeignHeifCompression.
    
    The compression format to use inside a HEIF container.

This is assumed to use the same numbering as %heif_compression_format.
    
    HEVC - x265
    AVC - x264
    JPEG - jpeg
    AV1 - aom
    """
    
    HEVC = 'hevc'
    AVC = 'avc'
    JPEG = 'jpeg'
    AV1 = 'av1'


class Size(object):
    """Size.
    
    Controls whether an operation should upsize, downsize, both up and
downsize, or force a size.

See also: vips_thumbnail().
    
    BOTH - size both up and down
    UP - only upsize
    DOWN - only downsize
    FORCE - force size, that is, break aspect ratio
    """
    
    BOTH = 'both'
    UP = 'up'
    DOWN = 'down'
    FORCE = 'force'


class Intent(object):
    """Intent.
    
    The rendering intent. #VIPS_INTENT_ABSOLUTE is best for
scientific work, #VIPS_INTENT_RELATIVE is usually best for
accurate communication with other imaging libraries.
    
    PERCEPTUAL - perceptual rendering intent
    RELATIVE - relative colorimetric rendering intent
    SATURATION - saturation rendering intent
    ABSOLUTE - absolute colorimetric rendering intent
    """
    
    PERCEPTUAL = 'perceptual'
    RELATIVE = 'relative'
    SATURATION = 'saturation'
    ABSOLUTE = 'absolute'


class Kernel(object):
    """Kernel.
    
    The resampling kernels vips supports. See vips_reduce(), for example.
    
    NEAREST - The nearest pixel to the point.
    LINEAR - Convolve with a triangle filter.
    CUBIC - Convolve with a cubic filter.
    LANCZOS2 - Convolve with a two-lobe Lanczos kernel.
    LANCZOS3 - Convolve with a three-lobe Lanczos kernel.
    """
    
    NEAREST = 'nearest'
    LINEAR = 'linear'
    CUBIC = 'cubic'
    MITCHELL = 'mitchell'
    LANCZOS2 = 'lanczos2'
    LANCZOS3 = 'lanczos3'


class PCS(object):
    """PCS.
    
    Pick a Profile Connection Space for vips_icc_import() and
vips_icc_export(). LAB is usually best, XYZ can be more convenient in some
cases.
    
    LAB - use CIELAB D65 as the Profile Connection Space
    XYZ - use XYZ as the Profile Connection Space
    """
    
    LAB = 'lab'
    XYZ = 'xyz'


class OperationMorphology(object):
    """OperationMorphology.
    
    More like hit-miss, really.

See also: vips_morph().
    
    ERODE - true if all set
    DILATE - true if one set
    """
    
    ERODE = 'erode'
    DILATE = 'dilate'


class CombineMode(object):
    """CombineMode.
    
    See vips_draw_image() and so on.

Operations like vips_draw_image() need to be told how to combine images
from two sources.

See also: vips_join().
    
    SET - set pixels to the new value
    ADD - add pixels
    """
    
    SET = 'set'
    ADD = 'add'


class Token(object):
    """Token.
    
    """
    
    LEFT = 'left'
    RIGHT = 'right'
    STRING = 'string'
    EQUALS = 'equals'


class Saveable(object):
    """Saveable.
    
    See also: #VipsForeignSave.
    
    MONO - 1 band (eg. CSV)
    RGB - 1 or 3 bands (eg. PPM)
    RGBA - 1, 2, 3 or 4 bands (eg. PNG)
    RGBA_ONLY - 3 or 4 bands (eg. WEBP)
    RGB_CMYK - 1, 3 or 4 bands (eg. JPEG)
    ANY - any number of bands (eg. TIFF)
    """
    
    MONO = 'mono'
    RGB = 'rgb'
    RGBA = 'rgba'
    RGBA_ONLY = 'rgba-only'
    RGB_CMYK = 'rgb-cmyk'
    ANY = 'any'


class ImageType(object):
    """ImageType.
    
    """
    
    ERROR = 'error'
    NONE = 'none'
    SETBUF = 'setbuf'
    SETBUF_FOREIGN = 'setbuf-foreign'
    OPENIN = 'openin'
    MMAPIN = 'mmapin'
    MMAPINRW = 'mmapinrw'
    OPENOUT = 'openout'


