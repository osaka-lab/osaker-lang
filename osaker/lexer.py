from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .typings import TokenT

from sly import Lexer

from .logger import osaker_logger

__all__ = (
    "OsakerLexer",
)

class OsakerLexer(Lexer):
    tokens = {
        NAME, ASSIGN, LITERAL, TYPE_DEFINE, PLUS, TIMES, MINUS, DIVIDE, LPAREN, RPAREN, 
    }
    ignore = " \t"

    # Tokens
    NAME = r"[a-zA-Z_][a-zA-Z0-9_]*"
    ASSIGN = r"<--"
    TYPE_DEFINE = r"~"
    LITERAL = r"""^["'][^"']*["']$|^\d+(\.\d+)?$"""

    # Special symbols
    PLUS = r"\+"
    MINUS = r"-"
    TIMES = r"\*"
    DIVIDE = r"/"
    LPAREN = r"\("
    RPAREN = r"\)"

    # Ignored pattern
    ignore_newline = r"\n+"

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, token: TokenT):
        osaker_logger.error(f"Illegal character '{token.value[0]}'!")
        self.index += 1