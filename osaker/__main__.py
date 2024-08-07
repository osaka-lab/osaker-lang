from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import typer

app = typer.Typer(
    pretty_exceptions_enable = False, 
    help = "The Osaker programming language interpreter."
)

@app.command(help = "Execute osaka code.")
def execute_code(
    file: str = typer.Argument(help = "The path to the .osaka script."), 
):
    raise NotImplementedError()