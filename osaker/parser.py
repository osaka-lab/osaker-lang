from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Iterable

    from .token import Token

import random
from pprint import pformat
from devgoldyutils import LoggerAdapter, Colours

from .logger import osaker_logger
from .exception import OsakerSyntaxError

__all__ = (
    "OsakerParser"
)

logger = LoggerAdapter(osaker_logger, prefix = "Parser")

class OsakerParser():
    types: Dict[str, type] = {
        "chiyo": int,
        "nyan": str
    }

    def __init__(self):
        self._globals: Dict[str, object] = {}

        self.__reverse_types: Dict[type, type] = dict(
            (v, k) for k, v in self.types.items()
        )

    def parse(self, tokens: List[Token]) -> None:
        logger.debug(f"Tokens --> {pformat(tokens)}")

        for index, token in enumerate(tokens):

            if token.type == "OP_DEFINE":
                self.__parse_define(tokens, index)

        logger.debug(f"Globals --> {pformat(self._globals)}")

    def __parse_define(self, tokens: List[Token], index: int):
        tokens: Iterable[Token] = iter(tokens[1:])
        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "NAME":
            raise OsakerSyntaxError(
                "A name must be given for the variable you are trying to define after ':o'. For example: ':o apple'."
            )

        variable_token = next_token

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "ASSIGN":
            raise OsakerSyntaxError(
                "Assign, but assign what? A pipe bomb? You must " \
                    "declare the value you would like to assign after '<--'."
            )

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "LITERAL":
            raise OsakerSyntaxError(
                "Only literals can be assigned, so that means numbers or strings. To assign a string always " \
                    "wrap it in speech marks ('\"') like this: ':o apple <-- \"I'm a apple!\"' ~nyan"
            )

        literal_token = next_token

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "TYPE":
            _type = self.__guess_literal_type(literal_token.value)
            osaka_type = self.__reverse_types[_type]

            hint_value = Colours.ORANGE.apply(f'"{literal_token.value}"')

            if _type is int:
                hint_value = Colours.BLUE.apply(literal_token.value)

            hint_msg = f"Did you mean: {hint_value} ~ {Colours.CLAY.apply(osaka_type)}"

            raise OsakerSyntaxError(
                "The type of the literal must be defined! For example: '\"Hello, World!\" ~nyan'\n" 
                    + self.__format_hint(hint_msg)
            )

        type_define_token = next_token

        type_ = self.types[type_define_token.value]

        self._globals[variable_token.value] = type_(literal_token.value)

    def __guess_literal_type(self, literal: str) -> type:

        try:
            int(literal)
            return int
        except ValueError:
            pass

        return str

    def __format_hint(self, message: str) -> str:
        face = random.choice(["(˶˃ ᵕ ˂˶) .ᐟ.ᐟ", "(˶ᵔ ᵕ ᵔ˶)"])

        return f"\n   {Colours.PINK_GREY.apply(face)} {message}\n"