#!/usr/bin/env python3
"""
Generate pyvips type stubs.

This script generates .pyi stub files for pyvips using introspection.
Run this to regenerate type stubs after adding new operations.

Usage:
    python examples/generate_type_stubs.py

RATIONALE:
---------
Type stubs are generated rather than handwritten because:
1. pyvips is a binding around libvips C library, which evolves independently
2. libvips has 300+ operations with complex signatures
3. New operations are added to libvips frequently
4. Generation uses same introspection mechanism as doc generation
5. Ensures stubs stay synchronized with available operations

This approach follows the existing pattern used for:
- Enum generation (examples/gen-enums.py)
- Documentation generation (pyvips.Operation.generate_sphinx_all())
"""

import inspect
from pathlib import Path

import pyvips
from pyvips import GValue, Introspect, type_map, type_from_name, nickname_find
from pyvips import ffi, Error
from pyvips.voperation import _OPERATION_DEPRECATED


def gtype_to_python_type(name: str, gtype: int, return_type: bool = False) -> str:
    """Map a gtype to Python type annotation string."""
    if (
        name in ("filename", "input_profile", "output_profile", "profile")
        and gtype == GValue.gstr_type
    ):
        return "str | Path"
    if not return_type and name in ("buffer",) and gtype == GValue.blob_type:
        return "_BufferLike"
    return GValue.gtype_to_python(gtype)


PYTHON_KEYWORDS = {
    "in",
    "min",
    "max",
    "type",
    "class",
    "def",
    "return",
    "import",
    "from",
    "as",
    "if",
    "else",
    "elif",
    "for",
    "while",
    "break",
    "continue",
    "pass",
    "raise",
    "try",
    "except",
    "finally",
    "with",
    "lambda",
    "and",
    "or",
    "not",
    "is",
    "None",
    "True",
    "False",
}


def escape_parameter_name(name: str) -> str:
    """Escape Python keywords in parameter names."""
    if name in PYTHON_KEYWORDS:
        return f"{name}_"
    return name


def generate_method_signature(operation_name: str) -> str | None:
    """Generate type signature for an operation method."""
    intro = Introspect.get(operation_name)

    if (intro.flags & _OPERATION_DEPRECATED) != 0:
        return None

    args_list = []

    if intro.member_x is not None:
        # Instance method: self comes first
        args_list.append("self")
    else:
        # Static/class method: no self
        pass

    # Required args (excluding member_x for instance methods)
    for name in intro.method_args:
        py_type = gtype_to_python_type(name, intro.details[name]["type"])
        args_list.append(f"{escape_parameter_name(name)}: {py_type}")

    # Optional args (excluding deprecated)
    if intro.doc_optional_input:
        args_list.append("*")
    for name in intro.doc_optional_input:
        py_type = gtype_to_python_type(name, intro.details[name]["type"])
        if name == "interpolate" and py_type == "GObject":
            py_type = "Interpolate"
        args_list.append(f"{escape_parameter_name(name)}: {py_type} = ...")

    # Optional output args
    for name in intro.doc_optional_output:
        args_list.append(f"{escape_parameter_name(name)}: bool = ...")

    args_str = ", ".join(args_list)
    # Return type
    output_types = [
        gtype_to_python_type(name, intro.details[name]["type"], return_type=True)
        for name in intro.required_output
    ]

    if len(output_types) == 0:
        return_type = "None"
    elif len(output_types) == 1:
        return_type = output_types[0]
    else:
        return_type = f"tuple[{', '.join(output_types)}]"

    # Optional output dicts can contain any metadata value type
    if len(intro.doc_optional_output) > 0 and return_type != "Image":
        return_type = (
            f"{return_type} | tuple[{', '.join(output_types + ['_MetadataDict'])}]"
        )

    if intro.member_x is not None:
        return f"    def {operation_name}({args_str}) -> {return_type}: ..."
    else:
        return f"    @staticmethod\n    def {operation_name}({args_str}) -> {return_type}: ..."


def generate_all_image_operations() -> str:
    """Generate type stubs for all dynamically generated Image methods."""

    # these names are aliased
    alias = ["crop"]
    alias_gtypes = {}
    for name in alias:
        gtype = pyvips.type_find("VipsOperation", name)
        alias_gtypes[gtype] = name

    all_names = []

    def add_name(gtype, a, b):
        if gtype in alias_gtypes:
            name = alias_gtypes[gtype]
        else:
            name = nickname_find(gtype)

        try:
            sig = generate_method_signature(name)
            if sig:
                all_names.append((name, sig))
        except Error:
            pass

        type_map(gtype, add_name)
        return ffi.NULL

    type_map(type_from_name("VipsOperation"), add_name)
    all_names.sort()

    # remove operations we have to wrap by hand
    exclude = ["scale", "ifthenelse", "bandjoin", "bandrank", "composite", "copy"]
    all_names = [(name, sig) for name, sig in all_names if name not in exclude]

    return "\n".join([sig for _, sig in all_names])


def generate_enums() -> str:
    """Generate the ``enums.py`` stub."""
    enum_names = sorted(n for n in dir(pyvips.enums) if not n.startswith("__"))
    enum_dict = dict(inspect.getmembers(pyvips.enums))
    enum_defs: list[str] = []
    for e in enum_names:
        et = enum_dict[e]
        emems = [(m, mval) for m, mval in et.__dict__.items() if not m.startswith("__")]
        enum_def = f"class {e}:\n" + "\n".join(
            f"    {name}: {type(value).__name__} = {value!r}" for name, value in emems
        )
        enum_defs.append(enum_def)

    return "\n\n".join(enum_defs) + "\n"


def generate_stub() -> str:
    """Generate the ``init.py`` stub."""

    enum_names = sorted(n for n in dir(pyvips.enums) if not n.startswith("__"))
    enums = ", ".join(f"{n} as {n}" for n in enum_names)

    stub = f"""import logging
from collections.abc import Mapping
from typing import Any, Callable

from .base import leak_set as leak_set, shutdown as shutdown, version as version, get_suffixes as get_suffixes, at_least_libvips as at_least_libvips, type_find as type_find, type_name as type_name, nickname_find as nickname_find, type_from_name as type_from_name, type_map as type_map, values_for_enum as values_for_enum, values_for_flag as values_for_flag, enum_dict as enum_dict, flags_dict as flags_dict
from .enums import {enums}
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
"""

    return stub


def generate_vimage() -> str:
    """Generate the ``vimage.py`` stub."""

    enum_names = sorted(n for n in dir(pyvips.enums) if not n.startswith("__"))
    enums = ", ".join(f"{n} as {n}" for n in enum_names)

    stub = f'''"""Type stubs for pyvips.

# flake8: noqa: E501

This file is automatically generated by examples/generate_type_stubs.py.

To regenerate after libvips updates:
    python examples/generate_type_stubs.py
"""

from pathlib import Path
from types import TracebackType
from typing import Any, Protocol, TypeAlias

import numpy as np  # type: ignore[import-not-found]

from PIL.Image import Image as PILImage  # type: ignore

from .enums import {enums}
from .error import Error as Error
from .vinterpolate import Interpolate
from .vobject import VipsObject
from .vsource import Source
from .vtarget import Target

class _ArrayInterface(Protocol):
    @property
    def __array_interface__(self) -> dict[str, Any]: ...

class _Array(Protocol):
    def __array__(self, dtype: np.dtype | None = None, copy: bool | None = None) -> Any: ...

# Common type aliases
_NumberLike = int | float
_NumberLikeList = list[int] | list[float]
_NumberLike2DList = list[list[int]] | list[list[float]]

# Required forward reference; remove and replace the following unions with `type`
# statements once Python 3.12 becomes the minimum supported version.
_ImageAlias: TypeAlias = "Image"

_MetadataValue = bool | int | float | str | _ImageAlias | list[int] | list[float] | list[_ImageAlias]
_MetadataDict = dict[str, _MetadataValue]

_BufferLike = bytes | bytearray | memoryview
_ImageOperand = _ImageAlias | _NumberLike | _NumberLikeList

class Image(VipsObject):
    """Wrap a VipsImage object."""

    # Properties
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def bands(self) -> int: ...
    @property
    def format(self) -> str | BandFormat: ...
    @property
    def interpretation(self) -> str | Interpretation: ...
    @property
    def xres(self) -> float: ...
    @property
    def yres(self) -> float: ...
    @property
    def xoffset(self) -> int: ...
    @property
    def yoffset(self) -> int: ...

    # Metadata methods
    # GValue can return: bool, int, float, str, Image, list[int], list[float], list[Image]
    def get_gainmap(self) -> Image | None: ...
    def get_typeof(self, name: str) -> int: ...
    def get(self, name: str) -> _MetadataValue: ...
    def get_fields(self) -> list[str]: ...
    def set_type(self, gtype: int, name: str, value: _MetadataValue) -> None: ...
    def set(self, name: str, value: _MetadataValue) -> None: ...
    def remove(self, name: str) -> bool: ...

    # Constructors
    @staticmethod
    def new_from_file(vips_filename: str | Path, *, memory: bool = ..., access: Access | str = ..., fail: bool = ..., **kwargs: Any) -> Image: ...
    @staticmethod
    def new_from_buffer(data: _BufferLike, options: str, *, access: Access | str = ..., fail: bool = ..., **kwargs: Any) -> Image: ...
    @staticmethod
    def new_from_list(array: _NumberLikeList | _NumberLike2DList, scale: float = 1.0, offset: float = 0.0) -> Image: ...
    @classmethod
    def new_from_array(cls, obj: _NumberLikeList | _NumberLike2DList | _ArrayInterface | _Array, scale: float = 1.0, offset: float = 0.0, interpretation: str | Interpretation | None = None) -> Image: ...
    @staticmethod
    def new_from_memory(data: _BufferLike, width: int, height: int, bands: int, format: str | BandFormat) -> Image: ...
    @staticmethod
    def new_from_source(source: Source, options: str, **kwargs: Any) -> Image: ...
    @staticmethod
    def new_temp_file(format: str) -> Image: ...
    def new_from_image(self, value: _NumberLike | _NumberLikeList) -> Image: ...
    def copy_memory(self) -> Image: ...

    # Writers
    def write_to_file(self, vips_filename: str | Path, **kwargs: Any) -> None: ...
    def write_to_buffer(self, format_string: str, **kwargs: Any) -> bytes: ...
    def write_to_target(self, target: Target, format_string: str, **kwargs: Any) -> None: ...
    def write_to_memory(self) -> bytes: ...
    def write(self, other: Image) -> None: ...

    # Utility methods
    def invalidate(self) -> None: ...
    def set_progress(self, progress: bool) -> None: ...
    def set_kill(self, kill: bool) -> None: ...
    def copy(self, *, width: int = ..., height: int = ..., bands: int = ..., format: str | BandFormat = ..., coding: str | Coding = ..., interpretation: str | Interpretation = ..., xres: float = ..., yres: float = ..., xoffset: int = ..., yoffset: int = ...) -> Image: ...
    def tolist(self) -> list[list[float]]: ...
    def __array__(self, dtype: np.dtype | str | None = None, copy: bool | None = None) -> np.ndarray: ...
    def numpy(self, dtype: np.dtype | str | None = None) -> np.ndarray: ...
    def pil(self) -> PILImage: ...

    # Hand-written bindings with type hints
    def floor(self) -> Image: ...
    def ceil(self) -> Image: ...
    def rint(self) -> Image: ...
    def bandand(self) -> Image: ...
    def bandor(self) -> Image: ...
    def bandeor(self) -> Image: ...
    def bandsplit(self) -> list[Image]: ...
    def bandjoin(self, other: Image | _NumberLike | _NumberLikeList | list[Image | _NumberLike]) -> Image: ...
    def atan2(self, other: _ImageOperand) -> Image: ...
    def get_n_pages(self) -> int: ...
    def get_page_height(self) -> int: ...
    def pagesplit(self) -> list[Image]: ...
    def pagejoin(self, other: Image | list[Image]) -> Image: ...
    def composite(self, other: Image | list[Image], mode: str | BlendMode | list[str | BlendMode], *, compositing_space: Interpretation = ..., premultiplied: bool = ..., x: list[int] | int = ..., y: list[int] | int = ...) -> Image: ...
    def bandrank(self, other: Image | list[Image], *, index: int = ...) -> Image: ...
    def maxpos(self) -> tuple[float, int, int]: ...
    def minpos(self) -> tuple[float, int, int]: ...
    def real(self) -> Image: ...
    def imag(self) -> Image: ...
    def polar(self) -> Image: ...
    def rect(self) -> Image: ...
    def conj(self) -> Image: ...
    def sin(self) -> Image: ...
    def cos(self) -> Image: ...
    def tan(self) -> Image: ...
    def asin(self) -> Image: ...
    def acos(self) -> Image: ...
    def atan(self) -> Image: ...
    def sinh(self) -> Image: ...
    def cosh(self) -> Image: ...
    def tanh(self) -> Image: ...
    def asinh(self) -> Image: ...
    def acosh(self) -> Image: ...
    def atanh(self) -> Image: ...
    def log(self) -> Image: ...
    def log10(self) -> Image: ...
    def exp(self) -> Image: ...
    def exp10(self) -> Image: ...
    def erode(self, mask: Image | list[list[int]]) -> Image: ...
    def dilate(self, mask: Image | list[list[int]]) -> Image: ...
    def median(self, size: int) -> Image: ...
    def fliphor(self) -> Image: ...
    def flipver(self) -> Image: ...
    def rot90(self) -> Image: ...
    def rot180(self) -> Image: ...
    def rot270(self) -> Image: ...
    def hasalpha(self) -> bool: ...
    def ifthenelse(self, in1: Image | _NumberLike | _NumberLikeList | _NumberLike2DList, in2: Image | _NumberLike | _NumberLikeList | _NumberLike2DList, *, blend: bool = ...) -> Image: ...
    def scaleimage(self, *, log: bool = ..., exp: float = ...) -> Image: ...

    # Dynamically generated operations
{generate_all_image_operations()}

    # Operators
    def __repr__(self) -> str: ...
    def __getattr__(self, name: str) -> Any: ...
    def __enter__(self) -> Image: ...
    def __exit__(self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None) -> None: ...
    def __getitem__(self, arg: int | slice | list[int] | list[bool]) -> Image: ...
    def __call__(self, x: int, y: int) -> list[float]: ...
    # Arithmetic operators
    def __add__(self, other: _ImageOperand) -> Image: ...
    def __radd__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __sub__(self, other: _ImageOperand) -> Image: ...
    def __rsub__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __mul__(self, other: _ImageOperand) -> Image: ...
    def __rmul__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __div__(self, other: _ImageOperand) -> Image: ...
    def __rdiv__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __truediv__(self, other: _ImageOperand) -> Image: ...
    def __rtruediv__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __floordiv__(self, other: _ImageOperand) -> Image: ...
    def __rfloordiv__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __mod__(self, other: _ImageOperand) -> Image: ...
    def __pow__(self, other: _ImageOperand) -> Image: ...
    def __rpow__(self, other: _ImageOperand) -> Image: ...
    def __abs__(self) -> Image: ...
    def __lshift__(self, other: _ImageOperand) -> Image: ...
    def __rshift__(self, other: _ImageOperand) -> Image: ...
    def __and__(self, other: _ImageOperand) -> Image: ...
    def __rand__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __or__(self, other: _ImageOperand) -> Image: ...
    def __ror__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __xor__(self, other: _ImageOperand) -> Image: ...
    def __rxor__(self, other: _NumberLike | _NumberLikeList) -> Image: ...
    def __neg__(self) -> Image: ...
    def __pos__(self) -> Image: ...
    def __invert__(self) -> Image: ...
    # Comparison operators
    def __gt__(self, other: _ImageOperand) -> Image: ...
    def __ge__(self, other: _ImageOperand) -> Image: ...
    def __lt__(self, other: _ImageOperand) -> Image: ...
    def __le__(self, other: _ImageOperand) -> Image: ...
    def __eq__(self, other: Any) -> bool | Image: ...  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]
    def __ne__(self, other: Any) -> bool | Image: ...  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]

    # Compatibility (deprecated) methods
    def get_value(self, name: str) -> _MetadataValue: ...
    def set_value(self, name: str, value: _MetadataValue) -> None: ...
    def get_scale(self) -> float: ...
    def get_offset(self) -> float: ...
'''

    return stub


if __name__ == "__main__":
    stub_base = Path(__file__).parents[1] / "pyvips"

    # Write to pyvips/__init__.pyi
    stub_file = stub_base / "__init__.pyi"
    stub_file.write_text(generate_stub())
    print(f"Generated type stub at {stub_file}")

    # Write to pyvips/enums.pyi
    stub_file = stub_base / "enums.pyi"
    stub_file.write_text(generate_enums())
    print(f"Generated type stub at {stub_file}")

    # Write to pyvips/vimage.pyi
    stub_file = stub_base / "vimage.pyi"
    stub_file.write_text(generate_vimage())
    print(f"Generated type stub at {stub_file}")
