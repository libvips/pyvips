import logging
from typing import Any, Callable, ClassVar

from pyvips.vimage import Image
from pyvips.vobject import VipsObject

logger: logging.Logger

_REQUIRED: int
_CONSTRUCT: int
_SET_ONCE: int
_SET_ALWAYS: int
_INPUT: int
_OUTPUT: int
_DEPRECATED: int
_MODIFY: int

_OPERATION_NOCACHE: int
_OPERATION_DEPRECATED: int

class Introspect(object):
    description: str
    flags: int
    details: dict[str, dict[str, Any]]
    required_input: list[str]
    optional_input: list[str]
    required_output: list[str]
    optional_output: list[str]
    doc_optional_input: list[str]
    doc_optional_output: list[str]
    member_x: str | None
    method_args: list[str]

    _introspect_cache: ClassVar[dict[str, Introspect]]

    def __init__(self, operation_name: str) -> None: ...
    @classmethod
    def get(cls: type["Introspect"], operation_name: str) -> "Introspect": ...

def _find_inside(pred: Callable[[Any], bool], thing: Any) -> Any | None: ...

class Operation(VipsObject):
    _docstring_cache: ClassVar[dict[str, str]]

    def __init__(self, pointer: Any) -> None: ...
    @staticmethod
    def new_from_name(operation_name: str) -> "Operation": ...
    def set(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride, reportImplicitOverride]
        self,
        name: str,
        flags: int,
        match_image: Image | None,
        value: Any,
    ) -> None: ...
    @staticmethod
    def call(operation_name: str, *args: Any, **kwargs: Any) -> Any: ...
    @staticmethod
    def _argtype_to_python(name: str, type: Any) -> str: ...
    @staticmethod
    def generate_docstring(operation_name: str) -> str: ...
    @staticmethod
    def generate_sphinx(operation_name: str) -> str: ...
    @staticmethod
    def generate_sphinx_all() -> None: ...

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
