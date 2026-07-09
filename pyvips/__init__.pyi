import logging
from collections.abc import Mapping
from typing import Any, Callable

from .base import leak_set as leak_set, shutdown as shutdown, version as version, get_suffixes as get_suffixes, at_least_libvips as at_least_libvips, type_find as type_find, type_name as type_name, nickname_find as nickname_find, type_from_name as type_from_name, type_map as type_map, values_for_enum as values_for_enum, values_for_flag as values_for_flag, enum_dict as enum_dict, flags_dict as flags_dict
from .enums import Access as Access, Align as Align, Angle as Angle, Angle45 as Angle45, BandFormat as BandFormat, BlendMode as BlendMode, Coding as Coding, Combine as Combine, CombineMode as CombineMode, CompassDirection as CompassDirection, Direction as Direction, Extend as Extend, FailOn as FailOn, ForeignDzContainer as ForeignDzContainer, ForeignDzDepth as ForeignDzDepth, ForeignDzLayout as ForeignDzLayout, ForeignHeifCompression as ForeignHeifCompression, ForeignHeifEncoder as ForeignHeifEncoder, ForeignKeep as ForeignKeep, ForeignPdfPageBox as ForeignPdfPageBox, ForeignPngFilter as ForeignPngFilter, ForeignPpmFormat as ForeignPpmFormat, ForeignSubsample as ForeignSubsample, ForeignTiffCompression as ForeignTiffCompression, ForeignTiffPredictor as ForeignTiffPredictor, ForeignTiffResunit as ForeignTiffResunit, ForeignWebpPreset as ForeignWebpPreset, Intent as Intent, Interesting as Interesting, Interpretation as Interpretation, Kernel as Kernel, OperationBoolean as OperationBoolean, OperationComplex as OperationComplex, OperationComplex2 as OperationComplex2, OperationComplexget as OperationComplexget, OperationMath as OperationMath, OperationMath2 as OperationMath2, OperationMorphology as OperationMorphology, OperationRelational as OperationRelational, OperationRound as OperationRound, PCS as PCS, Precision as Precision, RegionShrink as RegionShrink, SdfShape as SdfShape, Size as Size, TextWrap as TextWrap
from .error import Error as Error, _to_bytes as _to_bytes, _to_string as _to_string, _to_string_copy as _to_string_copy
from .gobject import GObject as GObject
from .gvalue import GValue as GValue
from .vconnection import Connection as Connection
from .vimage import Image as Image
from .vinterpolate import Interpolate as Interpolate
from .vobject import VipsObject as VipsObject
from .voperation import Introspect as Introspect, Operation as Operation, cache_set_max as cache_set_max, cache_set_max_mem as cache_set_max_mem, cache_set_max_files as cache_set_max_files, cache_set_trace as cache_set_trace, cache_get_max as cache_get_max, cache_get_size as cache_get_size, cache_get_max_mem as cache_get_max_mem, cache_get_max_files as cache_get_max_files, block_untrusted_set as block_untrusted_set, operation_block_set as operation_block_set
from .vregion import Region as Region
from .vsource import Source as Source
from .vsourcecustom import SourceCustom as SourceCustom
from .vtarget import Target as Target
from .vtargetcustom import TargetCustom as TargetCustom

_MetadataValue = bool | int | float | str | Image | list[int] | list[float] | list[Image]
_MetadataDict = dict[str, _MetadataValue]

logger: logging.Logger

API_mode: bool

__version__: str

ffi: Any
glib_lib: Any
vips_lib: Any
gobject_lib: Any

_log_handler_id: int | None
_remove_handler: Callable[[bytes, int], Any]

def library_name(name: str, abi_number: int, lib_prefix: str = "lib") -> str: ...
def _log_handler_callback(
    domain: Any, level: int, message: Any, user_data: Any
) -> None: ...
def _remove_log_handler() -> None: ...

def call(operation_name: str, *args: Any, **kwargs: Any) -> Image | tuple[Image, _MetadataDict]: ...

class GLogLevelFlags:
    FLAG_RECURSION: int
    FLAG_FATAL: int

    LEVEL_ERROR: int
    LEVEL_CRITICAL: int
    LEVEL_WARNING: int
    LEVEL_MESSAGE: int
    LEVEL_INFO: int
    LEVEL_DEBUG: int

    LEVEL_TO_LOGGER: Mapping[int, int]
