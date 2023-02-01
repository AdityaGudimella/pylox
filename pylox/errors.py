import typing as t

import attrs
import rich

from pylox.token import Token


class PyloxError(Exception):
    """Base class for errors raised by PyLox."""


class PyloxReturn(Exception):
    """Raised to return a value from a function."""

    def __init__(self, value: t.Any) -> None:
        super().__init__()
        self.value = value


class PyloxReportableError(PyloxError):
    """Base class for errors that can be reported to the user."""

    def __init__(self, message: str, line: int):
        super().__init__(message)
        self.message = message
        self.line = line

    @classmethod
    def from_token(cls, message: str, token: Token) -> "PyloxReportableError":
        """Create a PyloxReportableError from a Token."""
        return cls(message=message, line=token.line)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        return f"{self.__class__.__name__}: Line: {self.line} {self.message}"

    def __rich__(self) -> str:
        """Return a rich representation of the error."""
        cls_name = self.__class__.__name__
        return f"[red]{cls_name}[/red]: [bold]Line: {self.line}[/bold] {self.message}"


class PyloxScanError(PyloxReportableError):
    """An error raised during Scanner pass."""


class PyloxParseError(PyloxReportableError):
    """An error raised during Parser pass."""


class PyloxResolverError(PyloxReportableError):
    """An error raised during Resolver pass."""


class PyloxRuntimeError(PyloxReportableError):
    """An error raised during Interpreter pass."""


@attrs.define()
class Errors:
    errors: list[PyloxReportableError] = attrs.field(factory=list)

    _has_error: bool = attrs.field(init=False, default=False)

    @property
    def has_error(self) -> bool:
        """Return True if any errors have been recorded."""
        return self._has_error

    def record(self, error: PyloxReportableError) -> PyloxReportableError:
        """Record an error."""
        self._has_error = True
        self.errors.append(error)
        return error

    def report(self) -> None:
        """Report all recorded errors."""
        for error in self.errors:
            rich.print(error)
