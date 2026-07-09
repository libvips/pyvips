import logging
from typing import Any

from pyvips.vconnection import Connection

logger: logging.Logger

class Target(Connection):
    def __init__(self, pointer: Any) -> None: ...
    @staticmethod
    def new_to_descriptor(descriptor: int) -> "Target": ...
    @staticmethod
    def new_to_file(filename: str) -> "Target": ...
    @staticmethod
    def new_to_memory() -> "Target": ...
