from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, Tuple

from pprint import pformat
from devgoldyutils import Colours

from .lexer import OsakerLexer
from .logger import osaker_logger
from .exception import OsakerError

__all__ = (
    "OsakerParser"
)

class OsakerParser():
    types = {
        "chiyo": int,
        "nyan": str
    }

    def __init__(self):
        self._globals: Dict[str, Tuple[object, str]] = {}

    def parse(self) -> None:
        ...