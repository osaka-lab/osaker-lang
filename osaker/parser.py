from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Generator, Any, Type, Iterable, Tuple

import random
from pprint import pformat
from devgoldyutils import LoggerAdapter, Colours, short_str
from pathlib import Path

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
    OsakerTypeError,
    OsakerModuleDoesntExist
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

            elif token.type == "OP_IMPORT":
                self.__parse_import(tokens, index)

        logger.debug(f"Globals --> {pformat(self._globals)}")

    def __parse_define(self, all_tokens: List[Token], index: int):
        tokens: Generator[Token] = iter(all_tokens[index + 1:])

        variable_token = self.__parse_name(
            tokens_after_operator = tokens,
            error_message = "A name must be given for the Ayumu object " \
                "you are trying to define after ':o'. \nFor example: ':o apple'."
        )

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "ASSIGN":
            hint_msg = f'Example: :o {variable_token.value} <-- "Hello World!" ~nyan'

            raise OsakerSyntaxError(
                "You can't just define an Ayumu object; you must assign something to it.\n"
                    + self.__format_hint(hint_msg)
            )

        value, osaka_type = self.__parse_literal_or_name(
            tokens_after_operator = tokens,
            all_tokens = all_tokens,
            token_no_exist_error_message = "Assign, but assign what? A pipe bomb? You must " \
                "declare the value you would like to assign after '<--'."
        )

        ayumu_object = AyumuObject(
            type = osaka_type,
            value = value
        )

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
                literal_representation = f'"{ayumu_object.value}"'

            if osaka_type == OsakaType.TOMO:

                if ayumu_object.value is True:
                    literal_representation = "yaa"
                else:
                    literal_representation = "nuh"

            literal_representation = osaka_type.get_resp_colour().apply(literal_representation)

            print(
                ">>", f"{Colours.BLUE.apply(name_token.value)} <-- {literal_representation} ~{Colours.CLAY.apply(osaka_type.name.lower())}"
            )

    def __parse_import(self, all_tokens: List[Token], index: int):
        tokens: Generator[Token] = iter(all_tokens[index + 2:])

        name_token = self.__parse_name(
            tokens_after_operator = tokens,
            error_message = "A name must be given for the namespace this osaka modules should be imported as! \n" \
                "'my_module' is the namespace in the example below: \n"
                    + self.__format_hint("Example: :+ my_module! <-- \"./my_module.osaka\" ~osaka")
        )

        if name_token.value[-1] != "!":
            hint_msg = 'Example: :o my_module! <-- \"./my_module.osaka\" ~osaka'

            raise OsakerSyntaxError(
                "You need to end a namespace with a \"!\".\n"
                    + self.__format_hint(hint_msg)
            )

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "ASSIGN":
            hint_msg = f'Example: :o {name_token.value} <-- \"./my_module.osaka\" ~osaka'

            raise OsakerSyntaxError(
                "You can't just define an Ayumu object; you must assign something to it.\n"
                    + self.__format_hint(hint_msg)
            )

        module, _ = self.__parse_literal_or_name(
            tokens_after_operator = tokens, 
            all_tokens = all_tokens,
            token_no_exist_error_message = "You need to assign a module path.",
            ignore_type = True
        )
        
        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "TYPE":
            hint_msg = f'Example: :o {name_token.value} <-- \"./my_module.osaka\" ~osaka'

            raise OsakerSyntaxError(
                "You need to assign a type.\n"
                    + self.__format_hint(hint_msg)
            )

        module = Path(module)

        if not module.exists():
            raise OsakerModuleDoesntExist(f"The given module path: {module} doesn't exist.")
        
        content = open(module, "r").read()
        
        parser = OsakerParser()
        lexer = OsakerLexer()

        parser.parse(lexer.tokenize(content))

        self._globals[f"{name_token.value}"] = parser._globals

        # I hope this is what you want :3, also add better error messsages!

    def __parse_name(self, tokens_after_operator: Generator[Token], error_message: str) -> Token:
        next_token = next(tokens_after_operator, None)

        if next_token is None or not next_token.type == "NAME":
            raise OsakerSyntaxError(error_message)

        return next_token

    def __parse_literal_or_name(
        self, 
        tokens_after_operator: Generator[Token], 
        all_tokens: List[Token], 
        token_no_exist_error_message: str,
        ignore_type: bool = False
    ) -> Tuple[Any, OsakaType]:
        tokens = tokens_after_operator

        next_token = next(tokens, None)

        if next_token is None:
            raise OsakerSyntaxError(token_no_exist_error_message)

        if not next_token.type.startswith("LITERAL") and next_token.type not in ["NAME", "OP_MATH"]:
            raise OsakerSyntaxError(
                "Expected either a literal (numbers, strings or booleans), a math operation (:m 1 + 1) or a variable " \
                    f"but instead we got a '{next_token.type}' token. Only literals, math operations and variables can be used.\n" \
                        + self.__format_hint("Example #1: \":o hello_text <-- \"Hewwo World!\" ~nyan\"")
                        + self.__format_hint("Example #2: \":o answer <-- :m 1 + 1 ~chiyo\"")
                        + self.__format_hint("Example #3: \":o age <-- number_x ~chiyo\"")
            )

        if next_token.type == "OP_MATH":
            evaluated_answer = self.__parse_math(tokens, all_tokens)

            return evaluated_answer, OsakaType.CHIYO

        elif next_token.type == "NAME":
            ayumu_object = self.__get_ayumu_object_or_error(next_token)

            return ayumu_object.value, ayumu_object.type

        literal_token = next_token
        literal_token_osaka_type = OsakaType.from_python_type(self.__guess_literal_type(literal_token.value))

        hint_representation = self.__tokens_to_string_representation(all_tokens, literal_token)
        hint_msg = f"Did you mean: {hint_representation} " \
            f"~{Colours.CLAY.apply(literal_token_osaka_type.name.lower())}"

        value = self.__clean_token_value(literal_token.type, literal_token.value)

        if not ignore_type:
            next_token = next(tokens, None)

            if next_token is None or not next_token.type == "TYPE":
                error_msg = "The type of the literal must be defined!\n"

                if literal_token.type == "NAME":
                    error_msg = "You must specify the type you expect to come out of that variable!\n"

                raise OsakerSyntaxError(
                    error_msg + self.__format_hint(hint_msg)
                )

            type_token = next_token
            type_token_clean_value = self.__clean_token_value(type_token.type, type_token.value)

            try:
                osaka_type = OsakaType.from_osaka_type_string(type_token_clean_value)

            except ValueError as e:
                raise OsakerSyntaxError(
                    f"Uhhhh, that type ('{type_token_clean_value}') doesn't exist lil bro! Error: {e}"
                )

            if not literal_token_osaka_type == osaka_type:
                raise OsakerIncorrectTypeError(
                    "Incorrect type was defined! The value " \
                        f"'{short_str(str(value))}' is not of type '{osaka_type.name}'!\n"
                            + self.__format_hint(hint_msg)
                )

        else:
            osaka_type = literal_token_osaka_type

        value = self.__cast_correct_type_or_error(value, osaka_type)

        return value, osaka_type

    def __parse_math(self, tokens_after_operator: Generator[Token], all_tokens: Iterable[Token]) -> int:
        tokens = tokens_after_operator

        left_number_value, left_number_osaka_type = self.__parse_literal_or_name(
            tokens,
            all_tokens,
            token_no_exist_error_message = "After the math operator (':m') should follow a " \
                "math expression containing ~chiyo types. \n" + self.__format_hint("Example: :o answer <-- :m 1 + 1 ~chiyo"),
            ignore_type = True
        )

        if not left_number_osaka_type == OsakaType.CHIYO:
            raise OsakerTypeError(
                f"The ayumu object or literal '{short_str(str(left_number_value))}' " \
                    "given for math is not of ~chiyo type!"
            )

        next_token = next(tokens, None)

        if next_token is None or next_token.type not in ["PLUS", "MINUS", "TIMES", "DIVIDE"]:
            raise OsakerSyntaxError(
                "Do you not know how to do math, huh? Where the FUCK is your operator, HUH?!?! " \
                    f"\nAn actual math operator (e.g. +, -, *, /) must be given after the literal ~chiyo '{left_number_value}'! \n" 
                        + self.__format_hint("Like this mf: :m 1 + 1 ~chiyo")
            )

        actual_math_operator = next_token

        right_number_value, right_number_osaka_type = self.__parse_literal_or_name(
            tokens,
            all_tokens,
            token_no_exist_error_message = "Bro! Are you mad? After the actual math operator (e.g. +, -, *, /) " \
                "should follow another ~chiyo type. How dumb can you be?! Fucking hell man! " \
                    "I ain't helping you this time.",
            ignore_type = True
        )

        if not right_number_osaka_type == OsakaType.CHIYO:
            raise OsakerTypeError(
                f"The ayumu object or literal '{short_str(str(right_number_value))}' " \
                    "given for math is not of ~chiyo type!"
            )

        next_token = next(tokens, None)

        if next_token is None or not next_token.type == "TYPE":
            raise OsakerSyntaxError(
                "You still need to define a type here!\n" 
                    + self.__format_hint("Example: 123 ~chiyo")
            )

        if actual_math_operator.type == "PLUS":
            return left_number_value + right_number_value

        elif actual_math_operator.type == "MINUS":
            return left_number_value - right_number_value

        elif actual_math_operator.type == "TIMES":
            return left_number_value * right_number_value

        elif actual_math_operator.type == "DIVIDE":
            return left_number_value / right_number_value

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

    def __tokens_to_string_representation(self, tokens: Iterable[Token], token_to_stop_at: Token) -> str:
        resp_string_list = []

        for token in tokens:

            # we pray this fucking works.
            if token.id == token_to_stop_at.id:
                resp_string_list.append(token.value)
                break

            resp_string_list.append(token.value)

        return " ".join(resp_string_list)

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

        value = self.__clean_token_value(osaka_type, value)

        try:
            return _type(value)
        except ValueError as e:
            raise OsakerParseError(
                f"Oh oh that wasn't supposed to happen. An incorrect osaka type was cast! The type '{osaka_type.name}' " \
                    f"cannot cast upon the value '{short_str(value)}'! \nError: {e}"
            )

    def __clean_token_value(
        self,
        token_type: str,
        token_value: str
    ) -> str:
        value = token_value

        if token_type == "TYPE":
            value = value.replace("~", "").replace("-", "")
        elif token_type == "LITERAL_STRING":
            value = value.replace('"', "").replace("'", "")

        return value

    def __format_hint(self, message: str) -> str:
        face = random.choice(["(˶˃ ᵕ ˂˶) .ᐟ.ᐟ", "(˶ᵔ ᵕ ᵔ˶)"])

        return f"\n   {Colours.PINK_GREY.apply(face)} {message}\n"