class GsfOutputCsvQuotingMode(object):
    NEVER = 'never'
    AUTO = 'auto'


class BandFormat(object):
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
    ERROR = 'error'
    NONE = 'none'
    LABQ = 'labq'
    RAD = 'rad'


class Interpretation(object):
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
    ERROR = 'error'
    SMALLTILE = 'smalltile'
    FATSTRIP = 'fatstrip'
    THINSTRIP = 'thinstrip'


class OperationRelational(object):
    EQUAL = 'equal'
    NOTEQ = 'noteq'
    LESS = 'less'
    LESSEQ = 'lesseq'
    MORE = 'more'
    MOREEQ = 'moreeq'


class OperationBoolean(object):
    AND = 'and'
    OR = 'or'
    EOR = 'eor'
    LSHIFT = 'lshift'
    RSHIFT = 'rshift'


class OperationMath2(object):
    POW = 'pow'
    WOP = 'wop'


class OperationComplex2(object):
    CROSS_PHASE = 'cross-phase'


class OperationMath(object):
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
    RINT = 'rint'
    CEIL = 'ceil'
    FLOOR = 'floor'


class OperationComplex(object):
    POLAR = 'polar'
    RECT = 'rect'
    CONJ = 'conj'


class OperationComplexget(object):
    REAL = 'real'
    IMAG = 'imag'


class Combine(object):
    MAX = 'max'
    SUM = 'sum'
    MIN = 'min'


class Access(object):
    RANDOM = 'random'
    SEQUENTIAL = 'sequential'
    SEQUENTIAL_UNBUFFERED = 'sequential-unbuffered'


class Extend(object):
    BLACK = 'black'
    COPY = 'copy'
    REPEAT = 'repeat'
    MIRROR = 'mirror'
    WHITE = 'white'
    BACKGROUND = 'background'


class CompassDirection(object):
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
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Align(object):
    LOW = 'low'
    CENTRE = 'centre'
    HIGH = 'high'


class Interesting(object):
    NONE = 'none'
    CENTRE = 'centre'
    ENTROPY = 'entropy'
    ATTENTION = 'attention'
    LOW = 'low'
    HIGH = 'high'


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


class Precision(object):
    INTEGER = 'integer'
    FLOAT = 'float'
    APPROXIMATE = 'approximate'


class ForeignDzLayout(object):
    DZ = 'dz'
    ZOOMIFY = 'zoomify'
    GOOGLE = 'google'
    IIIF = 'iiif'


class ForeignDzDepth(object):
    ONEPIXEL = 'onepixel'
    ONETILE = 'onetile'
    ONE = 'one'


class ForeignDzContainer(object):
    FS = 'fs'
    ZIP = 'zip'
    SZI = 'szi'


class RegionShrink(object):
    MEAN = 'mean'
    MEDIAN = 'median'
    MODE = 'mode'
    MAX = 'max'
    MIN = 'min'
    NEAREST = 'nearest'


class ForeignWebpPreset(object):
    DEFAULT = 'default'
    PICTURE = 'picture'
    PHOTO = 'photo'
    DRAWING = 'drawing'
    ICON = 'icon'
    TEXT = 'text'


class ForeignTiffCompression(object):
    NONE = 'none'
    JPEG = 'jpeg'
    DEFLATE = 'deflate'
    PACKBITS = 'packbits'
    CCITTFAX4 = 'ccittfax4'
    LZW = 'lzw'
    WEBP = 'webp'
    ZSTD = 'zstd'


class ForeignTiffPredictor(object):
    NONE = 'none'
    HORIZONTAL = 'horizontal'
    FLOAT = 'float'


class ForeignTiffResunit(object):
    CM = 'cm'
    INCH = 'inch'


class ForeignHeifCompression(object):
    HEVC = 'hevc'
    AVC = 'avc'
    JPEG = 'jpeg'
    AV1 = 'av1'


class Size(object):
    BOTH = 'both'
    UP = 'up'
    DOWN = 'down'
    FORCE = 'force'


class Intent(object):
    PERCEPTUAL = 'perceptual'
    RELATIVE = 'relative'
    SATURATION = 'saturation'
    ABSOLUTE = 'absolute'


class Kernel(object):
    NEAREST = 'nearest'
    LINEAR = 'linear'
    CUBIC = 'cubic'
    MITCHELL = 'mitchell'
    LANCZOS2 = 'lanczos2'
    LANCZOS3 = 'lanczos3'


class PCS(object):
    LAB = 'lab'
    XYZ = 'xyz'


class OperationMorphology(object):
    ERODE = 'erode'
    DILATE = 'dilate'


class CombineMode(object):
    SET = 'set'
    ADD = 'add'


class Token(object):
    LEFT = 'left'
    RIGHT = 'right'
    STRING = 'string'
    EQUALS = 'equals'


class Saveable(object):
    MONO = 'mono'
    RGB = 'rgb'
    RGBA = 'rgba'
    RGBA_ONLY = 'rgba-only'
    RGB_CMYK = 'rgb-cmyk'
    ANY = 'any'


class ImageType(object):
    ERROR = 'error'
    NONE = 'none'
    SETBUF = 'setbuf'
    SETBUF_FOREIGN = 'setbuf-foreign'
    OPENIN = 'openin'
    MMAPIN = 'mmapin'
    MMAPINRW = 'mmapinrw'
    OPENOUT = 'openout'


