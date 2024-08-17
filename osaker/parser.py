from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from .token import Token

from pprint import pprint

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

    def parse(self, tokens: List[Token]) -> None:
        pprint(tokens)