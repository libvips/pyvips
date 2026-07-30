import logging
from typing import Any, ClassVar

from pyvips import Image

_MetadataValue = bool | int | float | str | Image | list[int] | list[float] | list[Image]

logger: logging.Logger

class GValue(object):
    gbool_type: ClassVar[int]
    gint_type: ClassVar[int]
    guint64_type: ClassVar[int]
    gdouble_type: ClassVar[int]
    gstr_type: ClassVar[int]
    genum_type: ClassVar[int]
    gflags_type: ClassVar[int]
    gobject_type: ClassVar[int]
    image_type: ClassVar[int]
    array_int_type: ClassVar[int]
    array_double_type: ClassVar[int]
    array_image_type: ClassVar[int]
    refstr_type: ClassVar[int]
    blob_type: ClassVar[int]
    source_type: ClassVar[int]
    target_type: ClassVar[int]
    format_type: ClassVar[int]
    blend_mode_type: ClassVar[int]

    _gtype_to_python: ClassVar[dict[int, str]]

    pointer: Any
    gvalue: Any

    @staticmethod
    def gtype_to_python(gtype: int) -> str: ...
    @staticmethod
    def to_enum(gtype: int, value: str | int) -> int: ...
    @staticmethod
    def from_enum(gtype: int, enum_value: int) -> str: ...
    @staticmethod
    def to_flag(gtype: int, value: str | int) -> int: ...
    def __init__(self) -> None: ...
    def set_type(self, gtype: int) -> None: ...
    def set(self, value: _MetadataValue) -> None: ...
    def get(self) -> _MetadataValue: ...
