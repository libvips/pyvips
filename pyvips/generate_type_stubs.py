#!/usr/bin/env python3
"""
Generate pyvips type stubs.

This script generates .pyi stub files for pyvips using introspection.
Run this to regenerate type stubs after adding new operations.

Usage:
    python pyvips/generate_type_stubs.py

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

import typing
from typing import Any, Optional, Union

import pyvips
from pyvips import (
    GValue,
    Introspect,
    type_map,
    type_from_name,
    nickname_find,
    at_least_libvips,
)
from pyvips import ffi, Error, _to_bytes, _to_string


def gtype_to_python_type(gtype: int) -> str:
    """Map a gtype to Python type annotation string."""
    fundamental = pyvips.gobject_lib.g_type_fundamental(gtype)

    if fundamental == GValue.genum_type:
        name = pyvips.type_name(gtype)
        if name.startswith("Vips"):
            name = name[4:]
        return f"Union[str, {name}]"

    type_mapping = {
        GValue.gbool_type: "bool",
        GValue.gint_type: "int",
        GValue.guint64_type: "int",
        GValue.gdouble_type: "float",
        GValue.gstr_type: "str",
        GValue.refstr_type: "str",
        GValue.gflags_type: "int",
        GValue.gobject_type: "GObject",
        GValue.image_type: "Image",
        GValue.array_int_type: "list[int]",
        GValue.array_double_type: "list[float]",
        GValue.array_image_type: "list[Image]",
        GValue.blob_type: "str",
        GValue.source_type: "Source",
        GValue.target_type: "Target",
    }

    if gtype in type_mapping:
        return type_mapping[gtype]
    if fundamental in type_mapping:
        return type_mapping[fundamental]
    return "Any"


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


def generate_method_signature(operation_name: str) -> str:
    """Generate type signature for an operation method."""
    intro = Introspect.get(operation_name)

    if (intro.flags & 4) != 0:  # _OPERATION_DEPRECATED
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
        py_type = gtype_to_python_type(intro.details[name]["type"])
        args_list.append(f"{escape_parameter_name(name)}: {py_type}")

    # Optional args (excluding deprecated)
    for name in intro.doc_optional_input:
        py_type = gtype_to_python_type(intro.details[name]["type"])
        args_list.append(f"{escape_parameter_name(name)}: {py_type} = ...")

    # Optional output args
    for name in intro.doc_optional_output:
        args_list.append(f"{escape_parameter_name(name)}: bool = ...")

    args_str = ", ".join(args_list)

    # Return type
    output_types = [
        gtype_to_python_type(intro.details[name]["type"])
        for name in intro.required_output
    ]

    if len(output_types) == 0:
        return_type = "None"
    elif len(output_types) == 1:
        return_type = output_types[0]
    else:
        return_type = f"tuple[{', '.join(output_types)}]"

    # Optional output dicts can contain any metadata value type
    if len(intro.doc_optional_output) > 0:
        dict_value_type = (
            "Union[bool, int, float, str, Image, list[int], list[float], list[Image]]"
        )
        return_type = f"Union[{return_type}, tuple[{', '.join(output_types + [f'Dict[str, {dict_value_type}]'])}]]"

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
    exclude = ["scale", "ifthenelse", "bandjoin", "bandrank"]
    all_names = [(name, sig) for name, sig in all_names if name not in exclude]

    return "\n".join([sig for _, sig in all_names])


def get_all_enum_names() -> list[str]:
    """Get all enum type names from introspection."""

    enum_names = set()

    def add_enums(gtype, a, b):
        fundamental = pyvips.gobject_lib.g_type_fundamental(gtype)
        if fundamental == GValue.genum_type:
            name = pyvips.type_name(gtype)
            if name.startswith("Vips"):
                name = name[4:]
            enum_names.add(name)
        type_map(gtype, add_enums)
        return ffi.NULL

    type_map(type_from_name("VipsOperation"), add_enums)

    # Also add base enums
    enum_names.update(
        [
            "BandFormat",
            "Interpretation",
            "Kernel",
            "Coding",
            "Extend",
            "Align",
            "Direction",
            "Angle",
            "Angle45",
            "Access",
            "Shrink",
            "Intent",
            "PCS",
            "OperationBoolean",
            "OperationComplex",
            "OperationComplex2",
            "OperationComplexget",
            "OperationMath",
            "OperationMath2",
            "OperationMorphology",
            "OperationRelational",
            "OperationRound",
            "Interesting",
            "SdfShape",
            "TextWrap",
            "Combine",
            "CombineMode",
            "CompassDirection",
            "Precision",
            "FailOn",
            "BlendMode",
        ]
    )

    return sorted(enum_names)


def generate_stub() -> str:
    """Generate complete pyvips type stub."""

    # Get all enum names
    enum_names = get_all_enum_names()

    enum_classes = "\n".join([f"class {name}: ..." for name in enum_names])

    stub = f'''"""Type stubs for pyvips.

This file is automatically generated by pyvips/generate_type_stubs.py.

RATIONALE FOR GENERATION:
- pyvips is a binding around libvips C library
- libvips has 300+ operations that change frequently
- Manual stub maintenance would be unmaintainable
- Generation uses same introspection as docs/ enums
- Ensures stubs stay synchronized with available operations

To regenerate after libvips updates:
    python pyvips/generate_type_stubs.py
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, TypeVar, Union, overload

# Exception classes
class Error(Exception): ...

# GObject base classes
class GObject: ...
class GValue: ...

# Connection classes
class Source: ...
class Target: ...

# Enum classes
{enum_classes}


class Image:
    """Wrap a VipsImage object."""

    # Properties
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def bands(self) -> int: ...
    @property
    def format(self) -> Union[str, BandFormat]: ...
    @property
    def interpretation(self) -> Union[str, Interpretation]: ...
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
    def get_typeof(self, name: str) -> int: ...
    def get(self, name: str) -> Union[bool, int, float, str, Image, list[int], list[float], list[Image]]: ...
    def get_fields(self) -> List[str]: ...
    def set_type(self, gtype: int, name: str, value: Union[bool, int, float, str, Image, list[int], list[float], list[Image]]) -> None: ...
    def set(self, name: str, value: Union[bool, int, float, str, Image, list[int], list[float], list[Image]]) -> None: ...
    def remove(self, name: str) -> bool: ...

    # Constructors
    @staticmethod
    def new_from_file(vips_filename: str, **kwargs: object) -> Image: ...
    @staticmethod
    def new_from_buffer(data: Union[bytes, bytearray, memoryview], options: str, **kwargs: object) -> Image: ...
    @staticmethod
    def new_from_list(array: List[List[float]], scale: float =1.0, offset: float = 0.0) -> Image: ...
    @classmethod
    def new_from_array(cls, obj: Union[List, bytes, bytearray, memoryview], scale: float = 1.0, offset: float = 0.0, interpretation: Optional[Union[str, Interpretation]] = None) -> Image: ...
    @staticmethod
    def new_from_memory(data: Union[bytes, bytearray, memoryview], width: int, height: int, bands: int, format: Union[str, BandFormat]) -> Image: ...
    @staticmethod
    def new_from_source(source: Source, options: str, **kwargs: object) -> Image: ...
    @staticmethod
    def new_temp_file(format: str) -> Image: ...
    def new_from_image(self, value: Union[float, List[float]]) -> Image: ...
    def copy_memory(self) -> Image: ...

    # Writers
    def write_to_file(self, vips_filename: str, **kwargs: object) -> None: ...
    def write_to_buffer(self, format_string: str, **kwargs: object) -> bytes: ...
    def write_to_target(self, target: Target, format_string: str, **kwargs: object) -> None: ...
    def write_to_memory(self) -> bytes: ...
    def write(self, other: Image) -> None: ...

    # Utility methods
    def invalidate(self) -> None: ...
    def set_progress(self, progress: bool) -> None: ...
    def set_kill(self, kill: bool) -> None: ...
    def copy(self, **kwargs: object) -> Image: ...
    def tolist(self) -> List[List[float]]: ...
    # numpy is optional dependency - use TYPE_CHECKING guard
    def __array__(self, dtype: Optional[str] = None, copy: Optional[bool] = None) -> object: ...
    def numpy(self, dtype: Optional[str] = None) -> object: ...

    # Dynamically generated operations
'''

    stub += generate_all_image_operations()

    stub += """

    # Operator overloads
    def __add__(self, other: Union[Image, float, int]) -> Image: ...
    def __radd__(self, other: Union[float, int]) -> Image: ...
    def __sub__(self, other: Union[Image, float, int]) -> Image: ...
    def __rsub__(self, other: Union[float, int]) -> Image: ...
    def __mul__(self, other: Union[Image, float, int]) -> Image: ...
    def __rmul__(self, other: Union[float, int]) -> Image: ...
    def __truediv__(self, other: Union[Image, float, int]) -> Image: ...
    def __rtruediv__(self, other: Union[float, int]) -> Image: ...
    def __floordiv__(self, other: Union[Image, float, int]) -> Image: ...
    def __rfloordiv__(self, other: Union[float, int]) -> Image: ...
    def __mod__(self, other: Union[Image, float, int]) -> Image: ...
    def __pow__(self, other: Union[Image, float, int]) -> Image: ...
    def __rpow__(self, other: Union[Image, float, int]) -> Image: ...
    def __abs__(self) -> Image: ...
    def __neg__(self) -> Image: ...
    def __pos__(self) -> Image: ...
    def __invert__(self) -> Image: ...
    def __lshift__(self, other: Union[Image, float, int]) -> Image: ...
    def __rshift__(self, other: Union[Image, float, int]) -> Image: ...
    def __and__(self, other: Union[Image, float, int]) -> Image: ...
    def __rand__(self, other: Union[Image, float, int]) -> Image: ...
    def __or__(self, other: Union[Image, float, int]) -> Image: ...
    def __ror__(self, other: Union[Image, float, int]) -> Image: ...
    def __xor__(self, other: Union[Image, float, int]) -> Image: ...
    def __rxor__(self, other: Union[Image, float, int]) -> Image: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __gt__(self, other: Union[Image, float, int]) -> Image: ...
    def __ge__(self, other: Union[Image, float, int]) -> Image: ...
    def __lt__(self, other: Union[Image, float, int]) -> Image: ...
    def __le__(self, other: Union[Image, float, int]) -> Image: ...

    def __getitem__(self, arg: Union[int, slice, List[int], List[bool]]) -> Image: ...
    def __call__(self, x: int, y: int) -> List[float]: ...
    def __repr__(self) -> str: ...


class Operation: ...
class Introspect: ...

# Global functions
def cache_set_max(mx: int) -> None: ...
def cache_set_max_mem(mx: int) -> None: ...
def cache_set_max_files(mx: int) -> None: ...
def cache_set_trace(trace: bool) -> None: ...
def cache_get_max() -> int: ...
def cache_get_size() -> int: ...
def cache_get_max_mem() -> int: ...
def cache_get_max_files() -> int: ...
def block_untrusted_set(state: bool) -> None: ...
def operation_block_set(name: str, state: bool) -> None: ...

# Module-level constants
API_mode: bool
"""

    return stub


if __name__ == "__main__":
    # Generate stub
    stub_content = generate_stub()

    # Write to pyvips/__init__.pyi
    import os

    stub_file = os.path.join(os.path.dirname(__file__), "__init__.pyi")
    with open(stub_file, "w") as f:
        f.write(stub_content)

    print(f"Generated type stub at {stub_file}")
