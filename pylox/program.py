from pathlib import Path

import attrs
import rich

from pylox.errors import Errors
from pylox.nodes import Stmt
from pylox.parser import Parser
from pylox.token import Token


@attrs.define()
class Program:
    source: str

    errors: Errors = attrs.field(init=False, default=None)
    parser: Parser = attrs.field(init=False, default=None)

    @classmethod
    def from_path(cls, path: str) -> "Program":
        """Load a Lox script from a path."""
        source = Path(path).read_text()
        return Program(source)

    def __attrs_post_init__(self):
        self.errors = Errors()
        self.parser = Parser.from_source(self.source, errors=self.errors)

    def parse(self) -> list[Stmt]:
        """Parse a Lox script."""
        return self.parser.parse()

    def run(self):
        """Run a Lox script."""
        tokens = self.scan_tokens()

        for token in tokens:
            rich.print(f"[blue]{token}[/blue]")

        if self.has_error:
            raise RuntimeError("Lox script had errors.")

    def scan_tokens(self) -> list[Token]:
        """Return a list of tokens from Lox code."""
        rich.print(f"[bold yellow]Scanning:[/bold yellow] {self.source}")
        return []

    def error(self, line: int, message: str) -> None:
        """Report an error."""
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str) -> None:
        """Report a message."""
        rich.print(f"[bold red]{line} Error {where}: {message}[/bold red]")
        self.has_error = True
