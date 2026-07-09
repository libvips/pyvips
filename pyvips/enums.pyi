class Access:
    RANDOM: str = 'random'
    SEQUENTIAL: str = 'sequential'
    SEQUENTIAL_UNBUFFERED: str = 'sequential-unbuffered'

class Align:
    LOW: str = 'low'
    CENTRE: str = 'centre'
    HIGH: str = 'high'

class Angle:
    D0: str = 'd0'
    D90: str = 'd90'
    D180: str = 'd180'
    D270: str = 'd270'

class Angle45:
    D0: str = 'd0'
    D45: str = 'd45'
    D90: str = 'd90'
    D135: str = 'd135'
    D180: str = 'd180'
    D225: str = 'd225'
    D270: str = 'd270'
    D315: str = 'd315'

class BandFormat:
    NOTSET: str = 'notset'
    UCHAR: str = 'uchar'
    CHAR: str = 'char'
    USHORT: str = 'ushort'
    SHORT: str = 'short'
    UINT: str = 'uint'
    INT: str = 'int'
    FLOAT: str = 'float'
    COMPLEX: str = 'complex'
    DOUBLE: str = 'double'
    DPCOMPLEX: str = 'dpcomplex'

class BlendMode:
    CLEAR: str = 'clear'
    SOURCE: str = 'source'
    OVER: str = 'over'
    IN: str = 'in'
    OUT: str = 'out'
    ATOP: str = 'atop'
    DEST: str = 'dest'
    DEST_OVER: str = 'dest-over'
    DEST_IN: str = 'dest-in'
    DEST_OUT: str = 'dest-out'
    DEST_ATOP: str = 'dest-atop'
    XOR: str = 'xor'
    ADD: str = 'add'
    SATURATE: str = 'saturate'
    MULTIPLY: str = 'multiply'
    SCREEN: str = 'screen'
    OVERLAY: str = 'overlay'
    DARKEN: str = 'darken'
    LIGHTEN: str = 'lighten'
    COLOUR_DODGE: str = 'colour-dodge'
    COLOUR_BURN: str = 'colour-burn'
    HARD_LIGHT: str = 'hard-light'
    SOFT_LIGHT: str = 'soft-light'
    DIFFERENCE: str = 'difference'
    EXCLUSION: str = 'exclusion'

class Coding:
    ERROR: str = 'error'
    NONE: str = 'none'
    LABQ: str = 'labq'
    RAD: str = 'rad'

class Combine:
    MAX: str = 'max'
    SUM: str = 'sum'
    MIN: str = 'min'

class CombineMode:
    SET: str = 'set'
    ADD: str = 'add'

class CompassDirection:
    CENTRE: str = 'centre'
    NORTH: str = 'north'
    EAST: str = 'east'
    SOUTH: str = 'south'
    WEST: str = 'west'
    NORTH_EAST: str = 'north-east'
    SOUTH_EAST: str = 'south-east'
    SOUTH_WEST: str = 'south-west'
    NORTH_WEST: str = 'north-west'

class Direction:
    HORIZONTAL: str = 'horizontal'
    VERTICAL: str = 'vertical'

class Extend:
    BLACK: str = 'black'
    COPY: str = 'copy'
    REPEAT: str = 'repeat'
    MIRROR: str = 'mirror'
    WHITE: str = 'white'
    BACKGROUND: str = 'background'

class FailOn:
    NONE: str = 'none'
    TRUNCATED: str = 'truncated'
    ERROR: str = 'error'
    WARNING: str = 'warning'

class ForeignDzContainer:
    FS: str = 'fs'
    ZIP: str = 'zip'
    SZI: str = 'szi'

class ForeignDzDepth:
    ONEPIXEL: str = 'onepixel'
    ONETILE: str = 'onetile'
    ONE: str = 'one'

class ForeignDzLayout:
    DZ: str = 'dz'
    ZOOMIFY: str = 'zoomify'
    GOOGLE: str = 'google'
    IIIF: str = 'iiif'
    IIIF3: str = 'iiif3'

class ForeignHeifCompression:
    HEVC: str = 'hevc'
    AVC: str = 'avc'
    JPEG: str = 'jpeg'
    AV1: str = 'av1'

class ForeignHeifEncoder:
    AUTO: str = 'auto'
    AOM: str = 'aom'
    RAV1E: str = 'rav1e'
    SVT: str = 'svt'
    X265: str = 'x265'

class ForeignKeep:
    NONE: int = 0
    EXIF: int = 1
    XMP: int = 2
    IPTC: int = 4
    ICC: int = 8
    OTHER: int = 16
    GAINMAP: int = 32
    ALL: int = 63

class ForeignPdfPageBox:
    MEDIA: str = 'media'
    CROP: str = 'crop'
    TRIM: str = 'trim'
    BLEED: str = 'bleed'
    ART: str = 'art'

class ForeignPngFilter:
    NONE: int = 8
    SUB: int = 16
    UP: int = 32
    AVG: int = 64
    PAETH: int = 128
    ALL: int = 248

class ForeignPpmFormat:
    PBM: str = 'pbm'
    PGM: str = 'pgm'
    PPM: str = 'ppm'
    PFM: str = 'pfm'
    PNM: str = 'pnm'

class ForeignSubsample:
    AUTO: str = 'auto'
    ON: str = 'on'
    OFF: str = 'off'

class ForeignTiffCompression:
    NONE: str = 'none'
    JPEG: str = 'jpeg'
    DEFLATE: str = 'deflate'
    PACKBITS: str = 'packbits'
    CCITTFAX4: str = 'ccittfax4'
    LZW: str = 'lzw'
    WEBP: str = 'webp'
    ZSTD: str = 'zstd'
    JP2K: str = 'jp2k'

class ForeignTiffPredictor:
    NONE: str = 'none'
    HORIZONTAL: str = 'horizontal'
    FLOAT: str = 'float'

class ForeignTiffResunit:
    CM: str = 'cm'
    INCH: str = 'inch'

class ForeignWebpPreset:
    DEFAULT: str = 'default'
    PICTURE: str = 'picture'
    PHOTO: str = 'photo'
    DRAWING: str = 'drawing'
    ICON: str = 'icon'
    TEXT: str = 'text'

class Intent:
    PERCEPTUAL: str = 'perceptual'
    RELATIVE: str = 'relative'
    SATURATION: str = 'saturation'
    ABSOLUTE: str = 'absolute'
    AUTO: str = 'auto'

class Interesting:
    NONE: str = 'none'
    CENTRE: str = 'centre'
    ENTROPY: str = 'entropy'
    ATTENTION: str = 'attention'
    LOW: str = 'low'
    HIGH: str = 'high'
    ALL: str = 'all'

class Interpretation:
    ERROR: str = 'error'
    MULTIBAND: str = 'multiband'
    B_W: str = 'b-w'
    HISTOGRAM: str = 'histogram'
    XYZ: str = 'xyz'
    LAB: str = 'lab'
    CMYK: str = 'cmyk'
    LABQ: str = 'labq'
    RGB: str = 'rgb'
    CMC: str = 'cmc'
    LCH: str = 'lch'
    LABS: str = 'labs'
    SRGB: str = 'srgb'
    YXY: str = 'yxy'
    FOURIER: str = 'fourier'
    RGB16: str = 'rgb16'
    GREY16: str = 'grey16'
    MATRIX: str = 'matrix'
    SCRGB: str = 'scrgb'
    HSV: str = 'hsv'
    OKLAB: str = 'oklab'
    OKLCH: str = 'oklch'

class Kernel:
    NEAREST: str = 'nearest'
    LINEAR: str = 'linear'
    CUBIC: str = 'cubic'
    MITCHELL: str = 'mitchell'
    LANCZOS2: str = 'lanczos2'
    LANCZOS3: str = 'lanczos3'
    MKS2013: str = 'mks2013'
    MKS2021: str = 'mks2021'

class OperationBoolean:
    AND: str = 'and'
    OR: str = 'or'
    EOR: str = 'eor'
    LSHIFT: str = 'lshift'
    RSHIFT: str = 'rshift'

class OperationComplex:
    POLAR: str = 'polar'
    RECT: str = 'rect'
    CONJ: str = 'conj'

class OperationComplex2:
    CROSS_PHASE: str = 'cross-phase'

class OperationComplexget:
    REAL: str = 'real'
    IMAG: str = 'imag'

class OperationMath:
    SIN: str = 'sin'
    COS: str = 'cos'
    TAN: str = 'tan'
    ASIN: str = 'asin'
    ACOS: str = 'acos'
    ATAN: str = 'atan'
    LOG: str = 'log'
    LOG10: str = 'log10'
    EXP: str = 'exp'
    EXP10: str = 'exp10'
    SINH: str = 'sinh'
    COSH: str = 'cosh'
    TANH: str = 'tanh'
    ASINH: str = 'asinh'
    ACOSH: str = 'acosh'
    ATANH: str = 'atanh'

class OperationMath2:
    POW: str = 'pow'
    WOP: str = 'wop'
    ATAN2: str = 'atan2'

class OperationMorphology:
    ERODE: str = 'erode'
    DILATE: str = 'dilate'

class OperationRelational:
    EQUAL: str = 'equal'
    NOTEQ: str = 'noteq'
    LESS: str = 'less'
    LESSEQ: str = 'lesseq'
    MORE: str = 'more'
    MOREEQ: str = 'moreeq'

class OperationRound:
    RINT: str = 'rint'
    CEIL: str = 'ceil'
    FLOOR: str = 'floor'

class PCS:
    LAB: str = 'lab'
    XYZ: str = 'xyz'

class Precision:
    INTEGER: str = 'integer'
    FLOAT: str = 'float'
    APPROXIMATE: str = 'approximate'

class RegionShrink:
    MEAN: str = 'mean'
    MEDIAN: str = 'median'
    MODE: str = 'mode'
    MAX: str = 'max'
    MIN: str = 'min'
    NEAREST: str = 'nearest'

class SdfShape:
    CIRCLE: str = 'circle'
    BOX: str = 'box'
    ROUNDED_BOX: str = 'rounded-box'
    LINE: str = 'line'

class Size:
    BOTH: str = 'both'
    UP: str = 'up'
    DOWN: str = 'down'
    FORCE: str = 'force'

class TextWrap:
    WORD: str = 'word'
    CHAR: str = 'char'
    WORD_CHAR: str = 'word-char'
    NONE: str = 'none'
