from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    ...

import typer
import logging
import readline
import platform
import traceback
from devgoldyutils import Colours

from . import __version__
from .lexer import OsakerLexer
from .errors import OsakerError
from .parser import OsakerParser
from .logger import osaker_logger

app = typer.Typer(
    pretty_exceptions_enable = False, 
    help = "The Osaker programming language interpreter."
)

@app.command(help = "Execute osaka code.")
def execute_code(
    file: Optional[str] = typer.Argument(
        None, help = "The path to the .osaka script."
    ),

    command_input: Optional[str] = typer.Option(
        None, "-c", "-i", help = "Passes the text directly to the interpreter as osaker code."
    ),
    debug: bool = typer.Option(False, help = "Log to the console useful information from the interpreter.")
):
    if debug:
        osaker_logger.setLevel(logging.DEBUG)

    lexer = OsakerLexer()
    parser = OsakerParser()

    if file is not None:
        file_content = open(file, "r").read()

        interpret_code_and_handle_exceptions(
            lexer = lexer,
            parser = parser,
            text = file_content,
            trace_on_error = debug
        )

        raise typer.Exit()

    if command_input is not None:
        interpret_code_and_handle_exceptions(
            lexer = lexer,
            parser = parser,
            text = command_input,
            trace_on_error = debug
        )

        raise typer.Exit()

    print(
        f"Osaker {__version__} [Python {platform.python_version()}] on '{platform.platform()}'\n" \
            "  Type \"exit\" to quite the REPL.\n"
    )

    while True:

        try:
            text = input(f"{Colours.PURPLE}>>>{Colours.RESET} ")

        except EOFError as e:
            osaker_logger.error(
                f"\nAn error occurred taking in that input! Error: {e}"
            )

            raise typer.Exit(1)

        except KeyboardInterrupt:
            print("")
            continue

        if text == "exit":
            raise typer.Exit(0)

        interpret_code_and_handle_exceptions(
            lexer = lexer,
            parser = parser,
            text = text,
            trace_on_error = debug
        )

def interpret_code_and_handle_exceptions(
    lexer: OsakerLexer,
    parser: OsakerParser,
    text: str,
    trace_on_error: bool
) -> None:
    try:
        parser.parse(lexer.tokenize(text))

    except OsakerError as e:
        if trace_on_error:
            print(traceback.format_exc())

        osaker_logger.error(
            f"{Colours.BOLD_RED}{e.__class__.__name__}:{Colours.RESET} {e}"
        )