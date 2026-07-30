import logging
from collections.abc import Callable

from pyvips.vsource import Source

logger: logging.Logger

class SourceCustom(Source):
    def __init__(self) -> None: ...
    def on_read(self, handler: Callable[[int], bytes | None]) -> None: ...
    def on_seek(self, handler: Callable[[int, int], int]) -> None: ...
