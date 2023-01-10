import rich
import typer

from pylox.lox import Lox

app = typer.Typer()

@app.command()
def main(
    path: str = typer.Option("", help="Path to Lox source file", exists=True),
):
    """Run a Lox script or start an interactive REPL.

    path: Path to Lox source file. If not provided, an interactive REPL will be started.
    """
    if path:
        typer.echo(f"Running script: {path}")
        try:
            program = Lox.from_path(path)
            program.run()
        except RuntimeError:
            exit(65)
    else:
        run_prompt()

def run_prompt():
    """Start an interactive REPL."""
    try:
        while True:
            rich.print("[bold green]>>>[/bold green] ", end="")
            line = input()
            Lox(line).run()
    except KeyboardInterrupt:
        rich.print("\n[bold green]Goodbye![/bold green]")
        exit(0)
