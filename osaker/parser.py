from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List

    from .token import Token

from pprint import pformat
from devgoldyutils import LoggerAdapter

from .logger import osaker_logger
from .exception import OsakerParseError

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
                next_token = tokens[index + 1]

                if not next_token.type == "NAME":
                    raise OsakerParseError(
                        f"A name must be given for the variable you are trying to define after ':o'. For example: ':o apple'."
                    )

                variable_token = next_token

                next_token = tokens[index + 2]

                if not next_token.type == "ASSIGN":
                    raise OsakerParseError(
                        f"Assign, but assign what? A pipe bomb? You must " \
                            "declare the value you would like to assign after '<--'."
                    )

                next_token = tokens[index + 3]

                if not next_token.type == "LITERAL":
                    raise OsakerParseError(
                        f"Only literals can be assigned, so that means numbers or strings. To assign a string always " \
                            "wrap it in speech marks ('\"') like this: ':o apple <-- \"I'm a apple!\"' ~nyan"
                    )

                literal_token = next_token

                next_token = tokens[index + 4]

                if not next_token.type == "TYPE":
                    raise OsakerParseError(
                        f"The type of the literal must be defined! For example: '\"Hello, World!\" ~nyan'"
                    )

                type_define_token = next_token

                type_ = self.types[type_define_token.value]

                self._globals[variable_token.value] = type_(literal_token.value)

        logger.debug(f"Globals --> {pformat(self._globals)}")