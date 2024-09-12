from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Iterable

    from .token import Token

from pprint import pformat
from devgoldyutils import LoggerAdapter

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
            raise OsakerSyntaxError(
                "The type of the literal must be defined! For example: '\"Hello, World!\" ~nyan'"
            )

        type_define_token = next_token

        type_ = self.types[type_define_token.value]

        self._globals[variable_token.value] = type_(literal_token.value)