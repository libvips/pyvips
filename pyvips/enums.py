# libvips enums -- this file is generated automatically
# flake8: noqa: E501


class BandFormat(object):
    """BandFormat.

The format used for each band element.

Each corresponds to a native C type for the current machine. For example,
:class:`.enums.BandFormat.USHORT` is `unsigned short`.

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

The various Porter-Duff and PDF blend modes. See :meth:`.Image.composite`,
for example.

The Cairo docs have [a nice explanation of all the blend
modes](https://www.cairographics.org/operators).

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
three-band float image of type :class:`.enums.Interpretation.LAB` should have its
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

    LABQ (str): implies :class:`.enums.Coding.LABQ`

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


class OperationRelational(object):
    """OperationRelational.

See also: :meth:`.Image.relational`.

Attributes:

    EQUAL (str): `==`

    NOTEQ (str): `!=`

    LESS (str): `<`

    LESSEQ (str): `<=`

    MORE (str): `>`

    MOREEQ (str): `>=`

    """

    EQUAL = 'equal'
    NOTEQ = 'noteq'
    LESS = 'less'
    LESSEQ = 'lesseq'
    MORE = 'more'
    MOREEQ = 'moreeq'


class OperationBoolean(object):
    """OperationBoolean.

See also: :meth:`.Image.boolean`.

Attributes:

    AND (str): `&`

    OR (str): `|`

    EOR (str): `^`

    LSHIFT (str): `>>`

    RSHIFT (str): `<<`

    """

    AND = 'and'
    OR = 'or'
    EOR = 'eor'
    LSHIFT = 'lshift'
    RSHIFT = 'rshift'


class OperationMath2(object):
    """OperationMath2.

See also: :meth:`.Image.math`.

Attributes:

    POW (str): `pow(left, right)`

    WOP (str): `pow(right, left)`

    ATAN2 (str): `atan2(left, right)`

    """

    POW = 'pow'
    WOP = 'wop'
    ATAN2 = 'atan2'


class OperationComplex2(object):
    """OperationComplex2.

See also: :meth:`.Image.complex2`.

Attributes:

    CROSS_PHASE (str): convert to polar coordinates

    """

    CROSS_PHASE = 'cross-phase'


class OperationMath(object):
    """OperationMath.

See also: :meth:`.Image.math`.

Attributes:

    SIN (str): `sin()`, angles in degrees

    COS (str): `cos()`, angles in degrees

    TAN (str): `tan()`, angles in degrees

    ASIN (str): `asin()`, angles in degrees

    ACOS (str): `acos()`, angles in degrees

    ATAN (str): `atan()`, angles in degrees

    LOG (str): log base e

    LOG10 (str): log base 10

    EXP (str): e to the something

    EXP10 (str): 10 to the something

    SINH (str): `sinh()`, angles in radians

    COSH (str): `cosh()`, angles in radians

    TANH (str): `tanh()`, angles in radians

    ASINH (str): `asinh()`, angles in radians

    ACOSH (str): `acosh()`, angles in radians

    ATANH (str): `atanh()`, angles in radians

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
    SINH = 'sinh'
    COSH = 'cosh'
    TANH = 'tanh'
    ASINH = 'asinh'
    ACOSH = 'acosh'
    ATANH = 'atanh'


class OperationRound(object):
    """OperationRound.

See also: :meth:`.Image.round`.

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

See also: :meth:`.Image.complex`.

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

See also: :meth:`.Image.complexget`.

Attributes:

    REAL (str): get real component

    IMAG (str): get imaginary component

    """

    REAL = 'real'
    IMAG = 'imag'


class Combine(object):
    """Combine.

How to combine values. See :meth:`.Image.compass`, for example.

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

The type of access an operation has to supply. See :meth:`.Image.tilecache`
and :class:`.Foreign`.

:class:`.enums.Access.RANDOM` means requests can come in any order.

:class:`.enums.Access.SEQUENTIAL` means requests will be top-to-bottom, but with some
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

See :meth:`.Image.embed`, :meth:`.Image.conv`, :meth:`.Image.affine` and so on.

When the edges of an image are extended, you can specify
how you want the extension done.

:class:`.enums.Extend.BLACK` -- new pixels are black, ie. all bits are zero.

:class:`.enums.Extend.COPY` -- each new pixel takes the value of the nearest edge
pixel

:class:`.enums.Extend.REPEAT` -- the image is tiled to fill the new area

:class:`.enums.Extend.MIRROR` -- the image is reflected and tiled to reduce hash
edges

:class:`.enums.Extend.WHITE` -- new pixels are white, ie. all bits are set

:class:`.enums.Extend.BACKGROUND` -- colour set from the @background property

We have to specify the exact value of each enum member since we have to
keep these frozen for back compat with vips7.

::: seealso
    :meth:`.Image.embed`.

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

A direction on a compass. Used for :meth:`.Image.gravity`, for example.

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

See :meth:`.Image.flip`, :meth:`.Image.join` and so on.

Operations like :meth:`.Image.flip` need to be told whether to flip left-right or
top-bottom.

::: seealso
    :meth:`.Image.flip`, :meth:`.Image.join`.

Attributes:

    HORIZONTAL (str): left-right

    VERTICAL (str): top-bottom

    """

    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Align(object):
    """Align.

See :meth:`.Image.join` and so on.

Operations like :meth:`.Image.join` need to be told whether to align images on the
low or high coordinate edge, or centre.

::: seealso
    :meth:`.Image.join`.

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
by :meth:`.Image.smartcrop`, for example, to decide what parts of the image to
keep.

:class:`.enums.Interesting.NONE` and :class:`.enums.Interesting.LOW` mean the same -- the
crop is positioned at the top or left. :class:`.enums.Interesting.HIGH` positions at
the bottom or right.

::: seealso
    :meth:`.Image.smartcrop`.

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

See :meth:`.Image.rot` and so on.

Fixed rotate angles.

::: seealso
    :meth:`.Image.rot`.

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

See :meth:`.Image.rot45` and so on.

Fixed rotate angles.

::: seealso
    :meth:`.Image.rot45`.

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


class TextWrap(object):
    """TextWrap.

Sets the word wrapping style for :meth:`.Image.text` when used with a maximum
width.

::: seealso
    :meth:`.Image.text`.

Attributes:

    WORD (str): wrap at word boundaries

    CHAR (str): wrap at character boundaries

    WORD_CHAR (str): wrap at word boundaries, but fall back to character boundaries if there is not enough space for a full word

    NONE (str): no wrapping

    """

    WORD = 'word'
    CHAR = 'char'
    WORD_CHAR = 'word-char'
    NONE = 'none'


class SdfShape(object):
    """SdfShape.

The SDF to generate,

::: seealso
    :meth:`.Image.sdf`.

Attributes:

    CIRCLE (str): a circle at @a, radius @r

    BOX (str): a box from @a to @b

    ROUNDED_BOX (str): a box with rounded @corners from @a to @b

    LINE (str): a line from @a to @b

    """

    CIRCLE = 'circle'
    BOX = 'box'
    ROUNDED_BOX = 'rounded-box'
    LINE = 'line'


class FailOn(object):
    """FailOn.

How sensitive loaders are to errors, from never stop (very insensitive), to
stop on the smallest warning (very sensitive).

Each one implies the ones before it, so :class:`.enums.FailOn.ERROR` implies
:class:`.enums.FailOn.TRUNCATED`.

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

:class:`.enums.ForeignPpmFormat.PBM` images are single bit.

:class:`.enums.ForeignPpmFormat.PGM` images are 8, 16, or 32-bits, one band.

:class:`.enums.ForeignPpmFormat.PPM` images are 8, 16, or 32-bits, three bands.

:class:`.enums.ForeignPpmFormat.PFM` images are 32-bit float pixels.

:class:`.enums.ForeignPpmFormat.PNM` images are anymap images -- the image format
is used to pick the saver.

Attributes:

    PBM (str): portable bitmap

    PGM (str): portable greymap

    PPM (str): portable pixmap

    PFM (str): portable float map

    PNM (str): portable anymap

    """

    PBM = 'pbm'
    PGM = 'pgm'
    PPM = 'ppm'
    PFM = 'pfm'
    PNM = 'pnm'


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

This is assumed to use the same numbering as `heif_compression_format`.

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


class ForeignHeifEncoder(object):
    """ForeignHeifEncoder.

The selected encoder to use.
If libheif hasn't been compiled with the selected encoder,
we will fallback to the default encoder for the compression format.

Attributes:

    AUTO (str): auto

    AOM (str): aom

    RAV1E (str): RAV1E

    SVT (str): SVT-AV1

    X265 (str): x265

    """

    AUTO = 'auto'
    AOM = 'aom'
    RAV1E = 'rav1e'
    SVT = 'svt'
    X265 = 'x265'


class Size(object):
    """Size.

Controls whether an operation should upsize, downsize, both up and
downsize, or force a size.

::: seealso
    :meth:`.Image.thumbnail`.

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

The rendering intent. :class:`.enums.Intent.ABSOLUTE` is best for
scientific work, :class:`.enums.Intent.RELATIVE` is usually best for
accurate communication with other imaging libraries.

Attributes:

    PERCEPTUAL (str): perceptual rendering intent

    RELATIVE (str): relative colorimetric rendering intent

    SATURATION (str): saturation rendering intent

    ABSOLUTE (str): absolute colorimetric rendering intent

    AUTO (str): the rendering intent that the profile suggests

    """

    PERCEPTUAL = 'perceptual'
    RELATIVE = 'relative'
    SATURATION = 'saturation'
    ABSOLUTE = 'absolute'
    AUTO = 'auto'


class Kernel(object):
    """Kernel.

The resampling kernels vips supports. See :meth:`.Image.reduce`, for example.

Attributes:

    NEAREST (str): The nearest pixel to the point.

    LINEAR (str): Convolve with a triangle filter.

    CUBIC (str): Convolve with a cubic filter.

    MITCHELL (str): Convolve with a Mitchell kernel.

    LANCZOS2 (str): Convolve with a two-lobe Lanczos kernel.

    LANCZOS3 (str): Convolve with a three-lobe Lanczos kernel.

    MKS2013 (str): Convolve with Magic Kernel Sharp 2013.

    MKS2021 (str): Convolve with Magic Kernel Sharp 2021.

    """

    NEAREST = 'nearest'
    LINEAR = 'linear'
    CUBIC = 'cubic'
    MITCHELL = 'mitchell'
    LANCZOS2 = 'lanczos2'
    LANCZOS3 = 'lanczos3'
    MKS2013 = 'mks2013'
    MKS2021 = 'mks2021'


class PCS(object):
    """PCS.

Pick a Profile Connection Space for :meth:`.Image.icc_import` and
:meth:`.Image.icc_export`. LAB is usually best, XYZ can be more convenient in some
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

::: seealso
    :meth:`.Image.morph`.

Attributes:

    ERODE (str): true if all set

    DILATE (str): true if one set

    """

    ERODE = 'erode'
    DILATE = 'dilate'


class CombineMode(object):
    """CombineMode.

See :meth:`.Image.draw_image` and so on.

Operations like :meth:`.Image.draw_image` need to be told how to combine images
from two sources.

::: seealso
    :meth:`.Image.join`.

Attributes:

    SET (str): set pixels to the new value

    ADD (str): add pixels

    """

    SET = 'set'
    ADD = 'add'


class ForeignKeep(object):
    """ForeignKeep.

Which metadata to retain.

Attributes:

    NONE (int): don't attach metadata

    EXIF (int): keep Exif metadata

    XMP (int): keep XMP metadata

    IPTC (int): keep IPTC metadata

    ICC (int): keep ICC metadata

    OTHER (int): keep other metadata (e.g. PNG comments and some TIFF tags)

    ALL (int): keep all metadata

    """

    NONE = 0
    EXIF = 1
    XMP = 2
    IPTC = 4
    ICC = 8
    OTHER = 16
    ALL = 31


class ForeignPngFilter(object):
    """ForeignPngFilter.

http://www.w3.org/TR/PNG-Filters.html
The values mirror those of png.h in libpng.

Attributes:

    NONE (int): no filtering

    SUB (int): difference to the left

    UP (int): difference up

    AVG (int): average of left and up

    PAETH (int): pick best neighbor predictor automatically

    ALL (int): adaptive

    """

    NONE = 8
    SUB = 16
    UP = 32
    AVG = 64
    PAETH = 128
    ALL = 248
