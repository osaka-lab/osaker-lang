from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Generator, Any, Type

import random
from pprint import pformat
from devgoldyutils import LoggerAdapter, Colours, short_str

import re
from .token import Token
from .lexer import OsakerLexer
from .logger import osaker_logger
from .osaka_type import OsakaType
from .ayumu_object import AyumuObject
from .errors import (
    OsakerSyntaxError, 
    OsakerError, 
    OsakerIncorrectTypeError, 
    OsakerParseError, 
    OsakerNameError,
    OsakerTypeError
)

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

        literal_token = self.__parse_assign_value(tokens, variable_token)

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

            literal_representation = str(ayumu_object.value)

            if osaka_type == OsakaType.NYAN:
                literal_representation = Colours.ORANGE.apply(f'"{ayumu_object.value}"')

            if osaka_type == OsakaType.CHIYO:
                literal_representation = Colours.CLAY.apply(str(ayumu_object.value))

            if osaka_type == OsakaType.TOMO:
                literal_representation = Colours.BLUE.apply(str(ayumu_object.value).lower())

            print(
                ">>", f"{Colours.BLUE.apply(name_token.value)} <-- {literal_representation} ~{Colours.CLAY.apply(osaka_type.name.lower())}"
            )

    def __parse_name(self, tokens_after_operator: Generator[Token], error_message: str) -> Token:
        next_token = next(tokens_after_operator, None)

        if next_token is None or not next_token.type == "NAME":
            raise OsakerSyntaxError(error_message)

        return next_token

    def __parse_assign_value(self, tokens_after_operator: Generator[Token], variable_token: Token) -> Token:
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

        if not next_token.type.startswith("LITERAL") and not next_token.type == "OP_MATH":
            hint_msg = """Example: ':o hello_text <-- \"Hewwo World!\" ~nyan' or ':o answer <-- :m 1 + 1 ~chiyo' """

            raise OsakerSyntaxError(
                "Only literals (numbers, strings or booleans) and math operations (:m 1 + 1) can be assigned! " \
                    "To assign a string always wrap it in speech marks ('\"').\n"
                        + self.__format_hint(hint_msg)
            )

        if next_token.type == "OP_MATH":
            answer = self.__parse_math(tokens)

            literal_token = Token(
                type = OsakaType.CHIYO, 
                value = str(answer)
            )

        else:
            literal_token = next_token

        return literal_token

    def __parse_type(self, tokens_after_operator: Generator[Token], literal_token: Token) -> OsakaType:
        tokens = tokens_after_operator

        next_token = next(tokens, None)
        literal_token_type = self.__guess_literal_type(literal_token.value)

        osaka_type = OsakaType.from_python_type(literal_token_type)

        hint_value = literal_token.value

        if osaka_type == OsakaType.NYAN:
            hint_value = Colours.ORANGE.apply(f'"{literal_token.value}"')

        elif osaka_type == OsakaType.CHIYO:
            hint_value = Colours.CLAY.apply(literal_token.value)

        elif osaka_type == OsakaType.TOMO:
            hint_value = Colours.BLUE.apply(literal_token.value)

        hint_msg = f"Did you mean: {hint_value} ~{Colours.CLAY.apply(osaka_type.name.lower())}"

        if next_token is None or not next_token.type == "TYPE":
            raise OsakerSyntaxError(
                "The type of the literal must be defined! For example: '\"Hello, World!\" ~nyan'\n" 
                    + self.__format_hint(hint_msg)
            )

        type_token = next_token

        try:
            osaka_type = OsakaType.from_osaka_type_string(type_token.value)

        except ValueError as e:
            raise OsakerSyntaxError(
                f"Uhhhh, that type ('{type_token.value}') doesn't exist bro! Error: {e}"
            )

        if literal_token_type is not osaka_type.value:
            raise OsakerIncorrectTypeError(
                "Incorrect type was defined! The value " \
                    f"'{literal_token.value}' is not of type '{osaka_type.name}'!\n"
                        + self.__format_hint(hint_msg)
            )

        return osaka_type

    def __parse_math(self, tokens_after_operator: Generator[Token]) -> int:
        tokens = tokens_after_operator

        next_token = next(tokens, None)

        if next_token is None or not next_token.type in ["LITERAL_NUMBER", "NAME"]:
            raise OsakerSyntaxError(
                "After the math operator (':m') should follow a math expression containing ~chiyo types. \n" 
                + self.__format_hint("Example: :o answer <-- :m 1 + 1 ~chiyo")
            )

        # TODO: put this into a function so I don't have to repeat this shit. I'm too sleepy for this shit...
        name_or_number_token = next_token

        if name_or_number_token.type == "NAME":
            name_token = name_or_number_token
            ayumu_object = self.__get_ayumu_object_or_error(name_or_number_token)

            if not ayumu_object.type == OsakaType.CHIYO:
                raise OsakerTypeError(
                    f"The ayumu object '{name_token.value}' " \
                        "given for math is not of ~chiyo type!"
                )

            left_number_value = ayumu_object.value

        else:
            left_number_value = name_or_number_token.value

        next_token = next(tokens, None)

        if next_token is None or not next_token.type in ["PLUS", "MINUS", "TIMES", "DIVIDE"]:
            raise OsakerSyntaxError(
                "Do you not know how to do math, huh? Where the FUCK is your operator, HUH?!?! " \
                    f"\nAn actual math operator (e.g. +, -, *, /) must be given after the literal ~chiyo '{left_number_literal.value}'. \n" 
                        + self.__format_hint("Like this: :m 1 + 1 ~chiyo")
            )

        actual_math_operator = next_token

        next_token = next(tokens, None)

        if next_token is None or not next_token.type in ["LITERAL_NUMBER", "NAME"]:
            raise OsakerSyntaxError(
                "Bro! Are you mad? After the actual math operator (e.g. +, -, *, /) " \
                    "should follow another ~chiyo type. How dumb can you be?! Fucking hell man! " \
                        "I ain't helping you this time."
            )

        name_or_number_token = next_token

        if name_or_number_token.type == "NAME":
            name_token = name_or_number_token
            ayumu_object = self.__get_ayumu_object_or_error(name_or_number_token)

            if not ayumu_object.type == OsakaType.CHIYO:
                raise OsakerTypeError(
                    f"The ayumu object '{name_token.value}' " \
                        "given for math is not of ~chiyo type!"
                )

            right_number_value = ayumu_object.value

        else:
            right_number_value = name_or_number_token.value

        left_number_cast_value: int = self.__cast_correct_type_or_error(left_number_value, OsakaType.CHIYO)
        right_number_cast_value: int = self.__cast_correct_type_or_error(right_number_value, OsakaType.CHIYO)

        if actual_math_operator.type == "PLUS":
            return left_number_cast_value + right_number_cast_value

        elif actual_math_operator.type == "MINUS":
            return left_number_cast_value - right_number_cast_value

        elif actual_math_operator.type == "TIMES":
            return left_number_cast_value * right_number_cast_value

        elif actual_math_operator.type == "DIVIDE":
            return left_number_cast_value / right_number_cast_value

        raise OsakerParseError(
            "Wait what, that math operator doesn't exist but it does exist? WHAT!"
        )

    def __get_ayumu_object_or_error(self, name_token: Token) -> AyumuObject:
        ayumu_object = self._globals.get(name_token.value)

        if ayumu_object is None:
            raise OsakerNameError(
                "An ayumu object (e.g. variable, function) " \
                    f"doesn't exist with the name '{name_token.value}'!"
            )

        return ayumu_object

    def __guess_literal_type(self, literal: str) -> Type[type]:

        if re.match(OsakerLexer.tokens["LITERAL_NUMBER"], literal):
            return int

        elif re.match(OsakerLexer.tokens["LITERAL_BOOL"], literal):
            return bool

        return str

    def __cast_correct_type_or_error(self, value: str, osaka_type: OsakaType) -> Any:
        _type = osaka_type.value

        if osaka_type == OsakaType.TOMO:

            if value in ["yes", "yaa", "ya"]:
                value = True
            elif value in ["no", "nuh", "nuhuh"]:
                value = False

        try:
            return _type(value)
        except ValueError as e:
            raise OsakerParseError(
                f"Oh oh that wasn't supposed to happen. An incorrect osaka type was cast! The type '{osaka_type.name}' " \
                    f"cannot cast upon the value '{short_str(value)}'! \nError: {e}"
            )

    def __format_hint(self, message: str) -> str:
        face = random.choice(["(˶˃ ᵕ ˂˶) .ᐟ.ᐟ", "(˶ᵔ ᵕ ᵔ˶)"])

        return f"\n   {Colours.PINK_GREY.apply(face)} {message}\n"