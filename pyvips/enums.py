# libvips enums -- this file is generated automatically
# flake8: noqa: E501


class BandFormat(object):
    """BandFormat.

The format used for each band element.

Each corresponds to a native C type for the current machine. For example,
#VIPS_FORMAT_USHORT is <type>unsigned short</type>.

Attributes:

    NOTSET (str): invalid setting

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

Attributes:

    CLEAR (str): where the second object is drawn, the first is removed

    SOURCE (str): the second object is drawn as if nothing were below

    OVER (str): the image shows what you would expect if you held two semi-transparent slides on top of each other

    IN (str): the first object is removed completely, the second is only drawn where the first was

    OUT (str): the second is drawn only where the first isn't

    ATOP (str): this leaves the first object mostly intact, but mixes both objects in the overlapping area

    DEST (str): leaves the first object untouched, the second is discarded completely

    DEST_OVER (str): like OVER, but swaps the arguments

    DEST_IN (str): like IN, but swaps the arguments

    DEST_OUT (str): like OUT, but swaps the arguments

    DEST_ATOP (str): like ATOP, but swaps the arguments

    XOR (str): something like a difference operator

    ADD (str): a bit like adding the two images

    SATURATE (str): a bit like the darker of the two

    MULTIPLY (str): at least as dark as the darker of the two inputs

    SCREEN (str): at least as light as the lighter of the inputs

    OVERLAY (str): multiplies or screens colors, depending on the lightness

    DARKEN (str): the darker of each component

    LIGHTEN (str): the lighter of each component

    COLOUR_DODGE (str): brighten first by a factor second

    COLOUR_BURN (str): darken first by a factor of second

    HARD_LIGHT (str): multiply or screen, depending on lightness

    SOFT_LIGHT (str): darken or lighten, depending on lightness

    DIFFERENCE (str): difference of the two

    EXCLUSION (str): somewhat like DIFFERENCE, but lower-contrast

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

Attributes:

    NONE (str): pixels are not coded

    LABQ (str): pixels encode 3 float CIELAB values as 4 uchar

    RAD (str): pixels encode 3 float RGB as 4 uchar (Radiance coding)

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

Attributes:

    MULTIBAND (str): generic many-band image

    B_W (str): some kind of single-band image

    HISTOGRAM (str): a 1D image, eg. histogram or lookup table

    XYZ (str): the first three bands are CIE XYZ

    LAB (str): pixels are in CIE Lab space

    CMYK (str): the first four bands are in CMYK space

    LABQ (str): implies #VIPS_CODING_LABQ

    RGB (str): generic RGB space

    CMC (str): a uniform colourspace based on CMC(1:1)

    LCH (str): pixels are in CIE LCh space

    LABS (str): CIE LAB coded as three signed 16-bit values

    SRGB (str): pixels are sRGB

    YXY (str): pixels are CIE Yxy

    FOURIER (str): image is in fourier space

    RGB16 (str): generic 16-bit RGB

    GREY16 (str): generic 16-bit mono

    MATRIX (str): a matrix

    SCRGB (str): pixels are scRGB

    HSV (str): pixels are HSV

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

Attributes:

    SMALLTILE (str): demand in small (typically 64x64 pixel) tiles

    FATSTRIP (str): demand in fat (typically 10 pixel high) strips

    THINSTRIP (str): demand in thin (typically 1 pixel high) strips

    """

    ERROR = 'error'
    SMALLTILE = 'smalltile'
    FATSTRIP = 'fatstrip'
    THINSTRIP = 'thinstrip'


class OperationRelational(object):
    """OperationRelational.

See also: vips_relational().

Attributes:

    EQUAL (str): ==

    NOTEQ (str): !=

    LESS (str): <

    LESSEQ (str): <=

    MORE (str): >

    MOREEQ (str): >=

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

Attributes:

    AND (str): &

    OR (str): |

    EOR (str): ^

    LSHIFT (str): >>

    RSHIFT (str): <<

    """

    AND = 'and'
    OR = 'or'
    EOR = 'eor'
    LSHIFT = 'lshift'
    RSHIFT = 'rshift'


class OperationMath2(object):
    """OperationMath2.

See also: vips_math().

Attributes:

    POW (str): pow( left, right )

    WOP (str): pow( right, left )

    ATAN2 (str): atan2( left, right )

    """

    POW = 'pow'
    WOP = 'wop'
    ATAN2 = 'atan2'


class OperationComplex2(object):
    """OperationComplex2.

See also: vips_complex2().

Attributes:

    CROSS_PHASE (str): convert to polar coordinates

    """

    CROSS_PHASE = 'cross-phase'


class OperationMath(object):
    """OperationMath.

See also: vips_math().

Attributes:

    SIN (str): sin(), angles in degrees

    COS (str): cos(), angles in degrees

    TAN (str): tan(), angles in degrees

    ASIN (str): asin(), angles in degrees

    ACOS (str): acos(), angles in degrees

    ATAN (str): atan(), angles in degrees

    SINH (str): sinh(), angles in radians

    COSH (str): cosh(), angles in radians

    TANH (str): tanh(), angles in radians

    ASINH (str): asinh(), angles in radians

    ACOSH (str): acosh(), angles in radians

    ATANH (str): atanh(), angles in radians

    LOG (str): log base e

    LOG10 (str): log base 10

    EXP (str): e to the something

    EXP10 (str): 10 to the something

    """

    SIN = 'sin'
    COS = 'cos'
    TAN = 'tan'
    ASIN = 'asin'
    ACOS = 'acos'
    ATAN = 'atan'
    SINH = 'sinh'
    COSH = 'cosh'
    TANH = 'tanh'
    ASINH = 'asinh'
    ACOSH = 'acosh'
    ATANH = 'atanh'
    LOG = 'log'
    LOG10 = 'log10'
    EXP = 'exp'
    EXP10 = 'exp10'


class OperationRound(object):
    """OperationRound.

See also: vips_round().

Attributes:

    RINT (str): round to nearest

    CEIL (str): the smallest integral value not less than

    FLOOR (str): largest integral value not greater than

    """

    RINT = 'rint'
    CEIL = 'ceil'
    FLOOR = 'floor'


class OperationComplex(object):
    """OperationComplex.

See also: vips_complex().

Attributes:

    POLAR (str): convert to polar coordinates

    RECT (str): convert to rectangular coordinates

    CONJ (str): complex conjugate

    """

    POLAR = 'polar'
    RECT = 'rect'
    CONJ = 'conj'


class OperationComplexget(object):
    """OperationComplexget.

See also: vips_complexget().

Attributes:

    REAL (str): get real component

    IMAG (str): get imaginary component

    """

    REAL = 'real'
    IMAG = 'imag'


class Combine(object):
    """Combine.

How to combine values. See vips_compass(), for example.

Attributes:

    MAX (str): take the maximum of the possible values

    SUM (str): sum all the values

    MIN (str): take the minimum value

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

Attributes:

    RANDOM (str): can read anywhere

    SEQUENTIAL (str): top-to-bottom reading only, but with a small buffer

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

Attributes:

    BLACK (str): extend with black (all 0) pixels

    COPY (str): copy the image edges

    REPEAT (str): repeat the whole image

    MIRROR (str): mirror the whole image

    WHITE (str): extend with white (all bits set) pixels

    BACKGROUND (str): extend with colour from the @background property

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

Attributes:

    CENTRE (str): centre

    NORTH (str): north

    EAST (str): east

    SOUTH (str): south

    WEST (str): west

    NORTH_EAST (str): north-east

    SOUTH_EAST (str): south-east

    SOUTH_WEST (str): south-west

    NORTH_WEST (str): north-west

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

Attributes:

    HORIZONTAL (str): left-right

    VERTICAL (str): top-bottom

    """

    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Align(object):
    """Align.

See vips_join() and so on.

Operations like vips_join() need to be told whether to align images on the
low or high coordinate edge, or centre.

See also: vips_join().

Attributes:

    LOW (str): align low coordinate edge

    CENTRE (str): align centre

    HIGH (str): align high coordinate edge

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

Attributes:

    NONE (str): do nothing

    CENTRE (str): just take the centre

    ENTROPY (str): use an entropy measure

    ATTENTION (str): look for features likely to draw human attention

    LOW (str): position the crop towards the low coordinate

    HIGH (str): position the crop towards the high coordinate

    ALL (str): everything is interesting

    """

    NONE = 'none'
    CENTRE = 'centre'
    ENTROPY = 'entropy'
    ATTENTION = 'attention'
    LOW = 'low'
    HIGH = 'high'
    ALL = 'all'


class Angle(object):
    """Angle.

See vips_rot() and so on.

Fixed rotate angles.

See also: vips_rot().

Attributes:

    D0 (str): no rotate

    D90 (str): 90 degrees clockwise

    D180 (str): 180 degree rotate

    D270 (str): 90 degrees anti-clockwise

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


class Precision(object):
    """Precision.

How accurate an operation should be.

Attributes:

    INTEGER (str): int everywhere

    FLOAT (str): float everywhere

    APPROXIMATE (str): approximate integer output

    """

    INTEGER = 'integer'
    FLOAT = 'float'
    APPROXIMATE = 'approximate'


class FailOn(object):
    """FailOn.

How sensitive loaders are to errors, from never stop (very insensitive), to
stop on the smallest warning (very sensitive).

Each one implies the ones before it, so #VIPS_FAIL_ON_ERROR implies
#VIPS_FAIL_ON_TRUNCATED.

Attributes:

    NONE (str): never stop

    TRUNCATED (str): stop on image truncated, nothing else

    ERROR (str): stop on serious error or truncation

    WARNING (str): stop on anything, even warnings

    """

    NONE = 'none'
    TRUNCATED = 'truncated'
    ERROR = 'error'
    WARNING = 'warning'


class ForeignPpmFormat(object):
    """ForeignPpmFormat.

The netpbm file format to save as.

#VIPS_FOREIGN_PPM_FORMAT_PBM images are single bit.

#VIPS_FOREIGN_PPM_FORMAT_PGM images are 8, 16, or 32-bits, one band.

#VIPS_FOREIGN_PPM_FORMAT_PPM images are 8, 16, or 32-bits, three bands.

#VIPS_FOREIGN_PPM_FORMAT_PFM images are 32-bit float pixels.

Attributes:

    PBM (str): portable bitmap

    PGM (str): portable greymap

    PPM (str): portable pixmap

    PFM (str): portable float map

    """

    PBM = 'pbm'
    PGM = 'pgm'
    PPM = 'ppm'
    PFM = 'pfm'


class ForeignSubsample(object):
    """ForeignSubsample.

Set subsampling mode.

Attributes:

    AUTO (str): prevent subsampling when quality >= 90

    ON (str): always perform subsampling

    OFF (str): never perform subsampling

    """

    AUTO = 'auto'
    ON = 'on'
    OFF = 'off'


class ForeignDzLayout(object):
    """ForeignDzLayout.

What directory layout and metadata standard to use.

Attributes:

    DZ (str): use DeepZoom directory layout

    ZOOMIFY (str): use Zoomify directory layout

    GOOGLE (str): use Google maps directory layout

    IIIF (str): use IIIF v2 directory layout

    IIIF3 (str): use IIIF v3 directory layout

    """

    DZ = 'dz'
    ZOOMIFY = 'zoomify'
    GOOGLE = 'google'
    IIIF = 'iiif'
    IIIF3 = 'iiif3'


class ForeignDzDepth(object):
    """ForeignDzDepth.

How many pyramid layers to create.

Attributes:

    ONEPIXEL (str): create layers down to 1x1 pixel

    ONETILE (str): create layers down to 1x1 tile

    ONE (str): only create a single layer

    """

    ONEPIXEL = 'onepixel'
    ONETILE = 'onetile'
    ONE = 'one'


class ForeignDzContainer(object):
    """ForeignDzContainer.

How many pyramid layers to create.

Attributes:

    FS (str): write tiles to the filesystem

    ZIP (str): write tiles to a zip file

    SZI (str): write to a szi file

    """

    FS = 'fs'
    ZIP = 'zip'
    SZI = 'szi'


class RegionShrink(object):
    """RegionShrink.

How to calculate the output pixels when shrinking a 2x2 region.

Attributes:

    MEAN (str): use the average

    MEDIAN (str): use the median

    MODE (str): use the mode

    MAX (str): use the maximum

    MIN (str): use the minimum

    NEAREST (str): use the top-left pixel

    """

    MEAN = 'mean'
    MEDIAN = 'median'
    MODE = 'mode'
    MAX = 'max'
    MIN = 'min'
    NEAREST = 'nearest'


class ForeignWebpPreset(object):
    """ForeignWebpPreset.

Tune lossy encoder settings for different image types.

Attributes:

    DEFAULT (str): default preset

    PICTURE (str): digital picture, like portrait, inner shot

    PHOTO (str): outdoor photograph, with natural lighting

    DRAWING (str): hand or line drawing, with high-contrast details

    ICON (str): small-sized colorful images

    TEXT (str): text-like

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

Use @predictor to set the lzw or deflate prediction, default horizontal.

Use @lossless to set WEBP lossless compression.

Use @level to set webp and zstd compression level.

Attributes:

    NONE (str): no compression

    JPEG (str): jpeg compression

    DEFLATE (str): deflate (zip) compression

    PACKBITS (str): packbits compression

    CCITTFAX4 (str): fax4 compression

    LZW (str): LZW compression

    WEBP (str): WEBP compression

    ZSTD (str): ZSTD compression

    JP2K (str): JP2K compression

    """

    NONE = 'none'
    JPEG = 'jpeg'
    DEFLATE = 'deflate'
    PACKBITS = 'packbits'
    CCITTFAX4 = 'ccittfax4'
    LZW = 'lzw'
    WEBP = 'webp'
    ZSTD = 'zstd'
    JP2K = 'jp2k'


class ForeignTiffPredictor(object):
    """ForeignTiffPredictor.

The predictor can help deflate and lzw compression. The values are fixed by
the tiff library.

Attributes:

    NONE (str): no prediction

    HORIZONTAL (str): horizontal differencing

    FLOAT (str): float predictor

    """

    NONE = 'none'
    HORIZONTAL = 'horizontal'
    FLOAT = 'float'


class ForeignTiffResunit(object):
    """ForeignTiffResunit.

Use inches or centimeters as the resolution unit for a tiff file.

Attributes:

    CM (str): use centimeters

    INCH (str): use inches

    """

    CM = 'cm'
    INCH = 'inch'


class ForeignHeifCompression(object):
    """ForeignHeifCompression.

The compression format to use inside a HEIF container.

This is assumed to use the same numbering as %heif_compression_format.

Attributes:

    HEVC (str): x265

    AVC (str): x264

    JPEG (str): jpeg

    AV1 (str): aom

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

Attributes:

    BOTH (str): size both up and down

    UP (str): only upsize

    DOWN (str): only downsize

    FORCE (str): force size, that is, break aspect ratio

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

Attributes:

    PERCEPTUAL (str): perceptual rendering intent

    RELATIVE (str): relative colorimetric rendering intent

    SATURATION (str): saturation rendering intent

    ABSOLUTE (str): absolute colorimetric rendering intent

    """

    PERCEPTUAL = 'perceptual'
    RELATIVE = 'relative'
    SATURATION = 'saturation'
    ABSOLUTE = 'absolute'


class Kernel(object):
    """Kernel.

The resampling kernels vips supports. See vips_reduce(), for example.

Attributes:

    NEAREST (str): The nearest pixel to the point.

    LINEAR (str): Convolve with a triangle filter.

    CUBIC (str): Convolve with a cubic filter.

    MITCHELL (str): Convolve with a Mitchell kernel.

    LANCZOS2 (str): Convolve with a two-lobe Lanczos kernel.

    LANCZOS3 (str): Convolve with a three-lobe Lanczos kernel.

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

Attributes:

    LAB (str): use CIELAB D65 as the Profile Connection Space

    XYZ (str): use XYZ as the Profile Connection Space

    """

    LAB = 'lab'
    XYZ = 'xyz'


class OperationMorphology(object):
    """OperationMorphology.

More like hit-miss, really.

See also: vips_morph().

Attributes:

    ERODE (str): true if all set

    DILATE (str): true if one set

    """

    ERODE = 'erode'
    DILATE = 'dilate'


class CombineMode(object):
    """CombineMode.

See vips_draw_image() and so on.

Operations like vips_draw_image() need to be told how to combine images
from two sources.

See also: vips_join().

Attributes:

    SET (str): set pixels to the new value

    ADD (str): add pixels

    """

    SET = 'set'
    ADD = 'add'


class Token(object):
    """Token.

Attributes:

    """

    LEFT = 'left'
    RIGHT = 'right'
    STRING = 'string'
    EQUALS = 'equals'


class Saveable(object):
    """Saveable.

See also: #VipsForeignSave.

Attributes:

    MONO (str): 1 band (eg. CSV)

    RGB (str): 1 or 3 bands (eg. PPM)

    RGBA (str): 1, 2, 3 or 4 bands (eg. PNG)

    RGBA_ONLY (str): 3 or 4 bands (eg. WEBP)

    RGB_CMYK (str): 1, 3 or 4 bands (eg. JPEG)

    ANY (str): any number of bands (eg. TIFF)

    """

    MONO = 'mono'
    RGB = 'rgb'
    RGBA = 'rgba'
    RGBA_ONLY = 'rgba-only'
    RGB_CMYK = 'rgb-cmyk'
    ANY = 'any'


class ImageType(object):
    """ImageType.

Attributes:

    """

    ERROR = 'error'
    NONE = 'none'
    SETBUF = 'setbuf'
    SETBUF_FOREIGN = 'setbuf-foreign'
    OPENIN = 'openin'
    MMAPIN = 'mmapin'
    MMAPINRW = 'mmapinrw'
    OPENOUT = 'openout'
