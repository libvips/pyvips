import logging
from collections.abc import Callable
from typing import Any

logger: logging.Logger

class GObject(object):
    _handles: list[Any]
    pointer: Any

    def __init__(self, pointer: Any) -> None: ...
    @staticmethod
    def new_pointer_from_gtype(gtype: int) -> Any: ...
    def signal_connect(self, name: str, callback: Callable[..., Any]) -> None: ...
