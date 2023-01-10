from pathlib import Path

import attrs
import rich

from pylox.token import Token


@attrs.define()
class Lox:
    source: str
    has_error: bool = attrs.field(default=False)

    @classmethod
    def from_path(cls, path: str) -> "Lox":
        """Load a Lox script from a path."""
        source = Path(path).read_text()
        return Lox(source)

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
