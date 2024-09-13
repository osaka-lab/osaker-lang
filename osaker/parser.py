from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Generator, Any

    from .token import Token

import random
from pprint import pformat
from devgoldyutils import LoggerAdapter, Colours, short_str

from .logger import osaker_logger
from .osaka_type import OsakaType
from .ayumu_object import AyumuObject
from .errors import OsakerSyntaxError, OsakerError, OsakerIncorrectTypeError

__all__ = (
    "OsakerParser"
)

logger = LoggerAdapter(osaker_logger, prefix = "Parser")

class OsakerParser():
    def __init__(self):
        self._globals: Dict[str, AyumuObject] = {}

    def parse(self, tokens: List[Token]) -> None:
        logger.debug(f"Tokens --> {pformat(tokens)}")

        for index, token in enumerate(tokens):

            if token.type == "OP_DEFINE":
                self.__parse_define(tokens, index)

            elif token.type == "OP_DELETE":
                self.__parse_delete(tokens, index)

            elif token.type == "OP_INSPECT":
                self.__parse_inspect(tokens, index)

        logger.debug(f"Globals --> {pformat(self._globals)}")

    def __parse_define(self, tokens: List[Token], index: int):
        tokens: Generator[Token] = iter(tokens[index + 1:])

        variable_token = self.__parse_name(
            tokens_after_operator = tokens,
            error_message = "A name must be given for the Ayumu object " \
                "you are trying to define after ':o'. \nFor example: ':o apple'."
        )

        literal_token = self.__parse_assign_literal(tokens, variable_token)

        osaka_type = self.__parse_type(tokens, literal_token)

        value = self.__cast_correct_type_or_error(literal_token.value, osaka_type)

        ayumu_object = AyumuObject(
            type = osaka_type,
            value = value
        )

        # TODO: Catch the type error.
        self._globals[variable_token.value] = ayumu_object

    def __parse_delete(self, tokens: List[Token], index: int):
        tokens: Generator[Token] = iter(tokens[index + 1:])

        name_token = self.__parse_name(
            tokens_after_operator = tokens,
            error_message = "A name must be given for the Ayumu object " \
                "you are trying to delete from memory after ':3'. \nFor example: ':3 !print'."
        )

        if name_token.value not in self._globals:
            raise OsakerError(
                f"'{name_token.value}' is not present in memory! Maybe you already deleted it?"
            )

        del self._globals[name_token.value]

    def __parse_inspect(self, tokens: List[Token], index: int):
        tokens: Generator[Token] = iter(tokens[index + 1:])

        name_token = self.__parse_name(
            tokens_after_operator = tokens,
            error_message = "A name must be given for the Ayumu object " \
                "you are trying to delete from memory after ':3'. \nFor example: ':3 !print'."
        )

        if name_token.value in self._globals:
            ayumu_object = self._globals[name_token.value]

            osaka_type = ayumu_object.type

            literal_representation = Colours.ORANGE.apply(f'"{ayumu_object.value}"')

            if osaka_type == OsakaType.CHIYO:
                literal_representation = Colours.BLUE.apply(str(ayumu_object.value))
            
            if osaka_type == OsakaType.TOMO:
                literal_representation = Colours.CLAY.apply(str(ayumu_object.value))

            print(
                ">>", f"{Colours.BLUE.apply(name_token.value)} <-- {literal_representation} ~{Colours.CLAY.apply(osaka_type.name.lower())}"
            )

    def __parse_name(self, tokens_after_operator: Generator[Token], error_message: str) -> Token:
        next_token = next(tokens_after_operator, None)

        if next_token is None or not next_token.type == "NAME":
            raise OsakerSyntaxError(error_message)

        return next_token

    def __parse_assign_literal(self, tokens_after_operator: Generator[Token], variable_token: Token) -> Token:
        tokens = tokens_after_operator

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "ASSIGN":
            hint_msg = f'Example: :o {variable_token.value} <-- "Hello World!" ~nyan'

            raise OsakerSyntaxError(
                "You can't just define an Ayumu object; you must assign something to it.\n"
                    + self.__format_hint(hint_msg)
            )

        next_token = next(tokens, None)

        if next_token is None:
            raise OsakerSyntaxError(
                "Assign, but assign what? A pipe bomb? You must " \
                    "declare the value you would like to assign after '<--'."
            )

        if not next_token.type == "LITERAL" and not next_token.type == "NAME":
            raise OsakerSyntaxError(
                "Only literals or name can be assigned, so that means numbers or strings. To assign a string always " \
                    "wrap it in speech marks ('\"') like this: \n':o apple <-- \"I'm a apple!\"' ~nyan"
            )

        literal_token = next_token

        return literal_token

    def __parse_type(self, tokens_after_operator: Generator[Token], literal_token: Token) -> OsakaType:
        tokens = tokens_after_operator

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "TYPE":
            _type = self.__guess_literal_type(literal_token.value)
            osaka_type = OsakaType.from_python_type(_type)

            hint_value = Colours.ORANGE.apply(f'"{literal_token.value}"')

            if _type is int:
                hint_value = Colours.BLUE.apply(literal_token.value)

            hint_msg = f"Did you mean: {hint_value} ~{Colours.CLAY.apply(osaka_type.name.lower())}"

            raise OsakerSyntaxError(
                "The type of the literal must be defined! For example: '\"Hello, World!\" ~nyan'\n" 
                    + self.__format_hint(hint_msg)
            )

        type_define_token = next_token

        try:
            osaka_type = OsakaType.from_osaka_type_string(type_define_token.value)

        except ValueError as e:
            raise OsakerSyntaxError(
                f"Uhhhh, that type ('{type_define_token.value}') doesn't exist bro! Error: {e}"
            )

        return osaka_type

    def __guess_literal_type(self, literal: str) -> type:

        try:
            int(literal)
            return int
        except (TypeError, ValueError):
            pass

        try:
            bool(literal)
            return bool
        except (TypeError, ValueError):
            pass

        return str

    def __cast_correct_type_or_error(self, value: str, osaka_type: OsakaType) -> Any:
        _type = osaka_type.value

        if value in ["yes", "yaa", "ya"]:
            value = True
        elif value in ["no", "nuh", "nuhuh"]:
            value = False

        try:
            return _type(value)
        except ValueError as e:
            raise OsakerIncorrectTypeError(
                f"An incorrect osaka type was cast! The type '{osaka_type.name}' " \
                    f"cannot cast upon the value '{short_str(value)}'! \nError: {e}"
            )

    def __format_hint(self, message: str) -> str:
        face = random.choice(["(˶˃ ᵕ ˂˶) .ᐟ.ᐟ", "(˶ᵔ ᵕ ᵔ˶)"])

        return f"\n   {Colours.PINK_GREY.apply(face)} {message}\n"