from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

    from .token import Token

from .logger import osaker_logger

__all__ = (
    "OsakerLexer",
)

class OsakerLexer():
    IGNORE = " \t"

    PLUS = r"\+"
    MINUS = r"-"
    TIMES = r"\*"
    DIVIDE = r"/"
    LPAREN = r"\("
    RPAREN = r"\)"

    ASSIGN = r"<--"
    TYPE_DEFINE = r"~"

    def tokenize(self) -> Tuple[Token]:
        ...