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
        "OP_DEFINE": ":>",

        "NAME": r"[a-zA-Z_][a-zA-Z0-9_]*",
        "ASSIGN": "<--",

        "LITERAL": r"(?<!<)-?\b\d+\b|(['\"])(?:\\.|[^\\])*?\1",

        "TYPE": r"~[a-zA-Z0-9_]+",

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
                            value = self.__manipulate_token_value(token_type, token_value)
                        )
                    )

                    position = match.end()
                    break

        return tokens

    def __manipulate_token_value(
        self, 
        token_type: str, 
        token_value: str
    ) -> str:
        value = None

        if token_type == "TYPE":
            value = token_value.replace("~", "")
        elif token_type == "LITERAL":
            value = token_value.replace('"', "").replace("'", "")
        else:
            value = token_value

        return value