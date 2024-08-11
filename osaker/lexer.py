from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Dict, Match

import re

from .token import Token
from .logger import osaker_logger
from .exception import OsakerError

__all__ = (
    "OsakerLexer",
)

class OsakerLexer():
    ignore = [
        " ", "\t"
    ]

    tokens: Dict[str, str] = {
        "NAME": r"[a-zA-Z_][a-zA-Z0-9_]*",
        "ASSIGN": r"<--",
        "TYPE_DEFINE": r"~",

        "PLUS": r"\+",
        "MINUS": r"-",
        "TIMES": r"\*",
        "DIVIDE": r"/",
        "LPAREN": r"\(",
        "RPAREN": r"\)",
    }

    def __init__(self) -> None:
        self.tokens_compiled: Dict[str, re.Pattern] = {}

        for token in self.tokens:
            self.tokens_compiled[token] = re.compile(self.tokens[token])

    def tokenize(self, string: str) -> List[Token]:
        tokens: List[Token] = []

        position = 0

        for char in string:

            if char in self.ignore:
                position += 1
                continue

            match = None

            for token_type in self.tokens_compiled:
                match = self.tokens_compiled[token_type].match(string, position)

                if match:
                    token_value = match.group(0)
                    tokens.append(
                        Token(
                            type = token_type, 
                            value = token_value
                        )
                    )

                    position = match.end()
                    break

            if match is None:
                raise OsakerError(
                    f"Osaker does not know of '{char}'! (The Osaker Lexer was not able to tokenise this)"
                )

        return tokens