import contextlib
from pathlib import Path

import rich
import typer
from pylox.ast_formatter import ASTFormatter
from pylox.parser import Parser

from pylox.program import Program
from pylox.errors import PyloxParseError, PyloxRuntimeError

app = typer.Typer()


@app.command()
def ast(
    file: str = typer.Option("", "-f", "--file", help="Path to Lox source file", exists=True),
    source: str = typer.Option("", "-s", "--source", help="Lox source code"),
):
    """Print the AST for a Lox script.

    path: Path to Lox source file.
    """
    if not file and not source:
        raise ValueError("Must provide either a file or source code")
    if file:
        if source:
            raise ValueError("Must provide either a file or source code, not both")
        source = Path(file).read_text()
    typer.echo(f"Printing AST for script: {file}")
    statements = Parser.from_source(source).parse()
    for statement in statements:
        rich.print(ASTFormatter().format(statement))


@app.command()
def file(
    path: str = typer.Argument(..., help="Path to Lox source file", exists=True),
    ast: bool = typer.Option(False, "-a", "--ast", help="Print the AST for the code"),
):
    """Run a Lox script.

    path: Path to Lox source file.
    """
    typer.echo(f"Running script: {path}")
    program = Program.from_path(path)
    if ast:
        print_ast(program)
    else:
        run_program(program)


@app.command()
def repl():
    """Start an interactive REPL."""
    try:
        while True:
            rich.print("[bold green]>>>[/bold green] ", end="")
            line = input()
            with contextlib.suppress(RuntimeError):
                Program.from_string(line).run()
    except KeyboardInterrupt:
        rich.print("\n[bold green]Goodbye![/bold green]")
        exit(0)


@app.command()
def command(
    command: str = typer.Argument(..., help="Lox code to run"),
    ast: bool = typer.Option(False, "-a", "--ast", help="Print the AST for the code"),
):
    """Run a Lox command.

    command: Lox code to run.
    """
    typer.echo(f"Running command: {command}")
    program = Program.from_string(command)
    if ast:
        print_ast(program)
    else:
        run_program(program)


def run_program(program: Program) -> None:
    """Run a Lox program."""
    try:
        program.run()
    except PyloxParseError:
        exit(65)
    except PyloxRuntimeError:
        exit(70)


def print_ast(program: Program) -> None:
    """Print the AST for a Lox program."""
    try:
        statements = program.parse()
    except PyloxParseError:
        exit(65)
    for statement in statements:
        rich.print(ASTFormatter().format(statement))


if __name__ == "__main__":
    program = Program.from_path("tests/resources/fibonacci_recursion.lox")
    program.run()
