import logging
from collections.abc import Buffer
from typing import Any

from .vconnection import Connection

logger: logging.Logger

class Source(Connection):
    def __init__(self, pointer: Any) -> None: ...
    @staticmethod
    def new_from_descriptor(descriptor: int) -> "Source": ...
    @staticmethod
    def new_from_file(filename: str) -> "Source": ...
    @staticmethod
    def new_from_memory(data: Buffer | memoryview | bytes | bytearray) -> "Source": ...

    _references: list[Any]
