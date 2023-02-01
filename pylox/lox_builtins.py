import time
import typing as t

import attrs

from pylox.environment import Environment
from pylox.interpreter import Interpreter, LoxCallable


@attrs.define()
class Clock(LoxCallable[[], float]):
    """Represents the clock function."""

    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: Interpreter) -> float:
        return time.time()

    def __str__(self) -> str:
        return "<builtin: Clock>"


class EnvironmentWithBuiltins(Environment):
    """An environment with builtins."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.define("clock", Clock())
