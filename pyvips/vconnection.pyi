import logging
from typing import Any

from pyvips.vobject import VipsObject

logger: logging.Logger

class Connection(VipsObject):
    def __init__(self, pointer: Any) -> None: ...
    def filename(self) -> str | None: ...
    def nick(self) -> str | None: ...
