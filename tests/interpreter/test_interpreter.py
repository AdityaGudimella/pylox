import typing as t

import pytest

from pylox import nodes as pn
from pylox.environment import Environment
from pylox.errors import Errors
from pylox.interpreter import Interpreter
from pylox.lox_builtins import EnvironmentWithBuiltins
from pylox.parser import Parser
from pylox.resolver import Resolver
from tests.interpreter.interpreter_test_params import INTERPRETER_SIDE_EFFECTS_PARAMS


@pytest.fixture()
def expr(source: str) -> list[pn.Stmt]:
    return Parser.from_source(source, errors=Errors()).parse()


@pytest.fixture()
def global_env() -> Environment:
    return EnvironmentWithBuiltins()


@pytest.fixture()
def interpreter(expr: list[pn.Stmt], global_env: Environment) -> Interpreter:
    interpreter = Interpreter(global_env=global_env)
    resolver = Resolver(interpreter=interpreter)
    resolver.resolve(*expr)
    return interpreter


@pytest.mark.parametrize(
    "source, expected",
    INTERPRETER_SIDE_EFFECTS_PARAMS,
)
def test_interpreter(
    interpreter: Interpreter, expr: list[pn.Stmt], expected: list[t.Any]
) -> None:
    """Test code having side effects."""
    interpreter.interpret(*expr)
    assert interpreter.test_console == expected
