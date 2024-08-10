from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, Tuple

    from .typings import TokenT

from sly import Parser
from pprint import pformat
from devgoldyutils import Colours

from .lexer import OsakerLexer
from .logger import osaker_logger
from .exception import OsakerError

__all__ = (
    "OsakerParser"
)

class OsakerParser(Parser):
    tokens = OsakerLexer.tokens

    precedence = (
        ("left", PLUS, MINUS),
        ("left", TIMES, DIVIDE),
        ("right", UMINUS),
    )

    types = {
        "chiyo": int,
        "nyan": str
    }

    def __init__(self):
        self._globals: Dict[str, Tuple[object, str]] = {}

    @_("NAME ASSIGN expr")
    def statement(self, p):
        print("uwu")
        print(">>", p.type)
        type_name, _type = p.type

        if not isinstance(p.expr, _type):
            raise OsakerError(
                f"The type '{type_name}' was defined but the expression '{p.expr}' is not of type '{type_name}'!"
            )

        self._globals[p.NAME] = (p.expr, type_name)

    @_("TYPE_DEFINE NAME")
    def type(self, p) -> Tuple[str, type]:
        _type = self.types.get(p.NAME)

        if _type is None:
            # TODO: This doesn't work so let's remove it I guess.
            raise OsakerError(
                f"The type definition '{p.NAME}' is invalid! Type should be one of: {self.types.values()}"
            )

        return (p.NAME, _type)

    @_("expr")
    def statement(self, p):
        print(p.expr)

    @_("expr PLUS expr")
    def expr(self, p):
        return p.expr0 + p.expr1

    @_("expr MINUS expr")
    def expr(self, p):
        return p.expr0 - p.expr1

    @_("expr TIMES expr")
    def expr(self, p):
        return p.expr0 * p.expr1

    @_("expr DIVIDE expr")
    def expr(self, p):
        return p.expr0 / p.expr1

    @_("MINUS expr %prec UMINUS")
    def expr(self, p):
        return -p.expr

    @_("LPAREN expr RPAREN")
    def expr(self, p):
        return p.expr

    @_("LITERAL type")
    def expr(self, p):
        type_name, _type = p.type

        if not isinstance(p.expr, _type):
            raise OsakerError(
                f"The type '{type_name}' was defined but the expression '{p.expr}' is not of type '{type_name}'!"
            )

        return _type(p.LITERAL)

    @_("NAME")
    def expr(self, p):
        try:
            value, type_name = self._globals[p.NAME]
            return f"{Colours.BLUE}{p.NAME} {Colours.WHITE}~{Colours.ORANGE}{type_name}{Colours.RESET} == {pformat(value)}"

        except LookupError:
            print(f"Undefined name {p.NAME!r}")
            return 0

    @_("LITERAL")
    def expr(self, p):
        return p.LITERAL

    def error(self, token: Optional[TokenT]):

        if token:
            line_number: Optional[int] = getattr(token, "lineno", None)
            character_index: Optional[int] = getattr(token, "index", None)

            token_recognise_error = f"We recognise '{token.value}' as the token '{token.type}'. " \
                "Is that correct? Check your syntax."

            if line_number and character_index:
                osaker_logger.error(
                    f"Syntax error on line '{line_number}' at character index " \
                        f"'{character_index}' ('{token.value}')! " + token_recognise_error
                )

            else:
                osaker_logger.error(f"Syntax error! " + token_recognise_error)

        else:
            osaker_logger.critical("Parse error in input! EOF\n")