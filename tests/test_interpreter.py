import typing as t

import pytest

from pylox.stmt import Stmt
from pylox.interpreter import Interpreter
from pylox.parser import Parser


@pytest.fixture()
def expr(source: str) -> list[Stmt]:
    return Parser.from_source(source).parse()


@pytest.mark.parametrize(
    "source, expected",
    [
        ("var expected = 1 + 2;", 3),
        ("var expected = 1 + 2 * 3;", 7),
        ("var a = 1; var expected = a;", 1),
        ("var a = 1; var b = a; var expected = b;", 1),
        ("var a = 1; var b = 2; var expected = a + b;", 3),
        (
            """
            // Calculate the 21st Fibonacci number.
            var a = 0;
            var temp;

            for (var b = 1; a < 10000; b = temp + b) {
                temp = a;
                a = b;
            }
            var expected = a;
            """,
            10946,
        )
    ],
)
def test_interpreter(expr: list[Stmt], expected: t.Any) -> None:
    """Since the interpreter does not return a value, we define a variable named
    `expected` and set it to the value we expect. Then we can assert that the
    `expected` variable has the value we expect by getting it from the interpreter's
    environment."""
    interpreter = Interpreter()
    interpreter.interpret(expr)
    assert interpreter.environment.test_get_var("expected") == expected
