from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    ...

import typer
import logging
import readline
import platform
from devgoldyutils import Colours

from . import __version__
from .lexer import OsakerLexer
from .parser import OsakerParser
from .logger import osaker_logger
from .exception import OsakerError

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
    debug: bool = typer.Option(help = "Log to the console useful information from the interpreter.")
):
    if debug:
        osaker_logger.setLevel(logging.DEBUG)

    if file is not None:
        raise typer.Exit() # TODO: Run code inside script file.

    lexer = OsakerLexer()
    parser = OsakerParser()

    if command_input is not None:
        interpret_code_and_handle_exceptions(
            lexer = lexer,
            parser = parser,
            text = command_input
        )

        raise typer.Exit()

    print(
        f"Osaker {__version__} [Python {platform.python_version()}] on '{platform.platform()}'"
    )

    while True:
        text = input(f"{Colours.PURPLE}>>>{Colours.RESET} ")

        interpret_code_and_handle_exceptions(
            lexer = lexer,
            parser = parser,
            text = text
        )

def interpret_code_and_handle_exceptions(
    lexer: OsakerLexer,
    parser: OsakerParser,
    text: str
) -> None:
    try:
        parser.parse(lexer.tokenize(text))

    except OsakerError as e:
        osaker_logger.error(
            f"{Colours.BOLD_RED}Osaker Exception:{Colours.RESET} {e}"
        )

        raise typer.Exit(1)

    except EOFError as e:
        osaker_logger.error(
            f"An error occurred taking in that input! Error: {e}"
        )

        raise typer.Exit(1)

    except KeyboardInterrupt as e:
        osaker_logger.error(
            f"You interrupted Osaka with your loud ass keyboard!"
        )

        raise typer.Exit(130)