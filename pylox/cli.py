import contextlib

import rich
import typer

from pylox import nodes as pn
from pylox.ast_formatter import ASTFormatter
from pylox.errors import PyloxParseError, PyloxRuntimeError
from pylox.program import Program

app = typer.Typer()


@app.command()
def file(
    path: str = typer.Argument(..., help="Path to Lox source file"),
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
                Program(line).run()
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
    program = Program(command)
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
        rich.print(pn.visit_node(statement, ASTFormatter()))


if __name__ == "__main__":
    program = Program.from_path("tests/resources/fibonacci_recursion.lox")
    program.run()
