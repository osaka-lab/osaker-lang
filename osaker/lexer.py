from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict

import re

from .token import Token

__all__ = (
    "OsakerLexer",
)

class OsakerLexer():
    ignore = [      
        " ", "\t"
    ]

    tokens: Dict[str, str] = {
        "OP_DELETE": ":3",
        "OP_DEFINE": r":[oO]",
        "OP_INSPECT": ":<",
        "OP_MATH": r":[mM]",

        "LITERAL_NUMBER": r"-?\b\d+\b",
        "LITERAL_STRING": r"(['\"])(?:\\.|[^\\])*?\1",
        "LITERAL_BOOL": r"\b(?:yes|yaa|ya|no|nuh|nuhuh)\b",

        "NAME": r"[!a-zA-Z_][a-zA-Z0-9_]*",
        "ASSIGN": "<--",

        "TYPE": r"[~-][a-zA-Z0-9_]+", # characters starting with either "-" or "~"

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

        for line_number, line in enumerate(string.splitlines()):

            position = 0

            for char in line:

                if char in self.ignore:
                    position += 1
                    continue

                match = None

                for token_type in self.tokens_compiled:
                    match = self.tokens_compiled[token_type].match(line, position)

                    if match:
                        token_value = match.group(0)
                        tokens.append(
                            Token(
                                type = token_type,
                                value = token_value,
                                line_number = line_number + 1,
                                character_number = position + 1
                            )
                        )

                        position = match.end()
                        break

        return tokens