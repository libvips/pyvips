from typing import Any

from pyvips.vobject import VipsObject

class Interpolate(VipsObject):
    def __init__(self, pointer: Any) -> None: ...
    @staticmethod
    def new(name: str) -> "Interpolate": ...
