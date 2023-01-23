import pytest
from pylox.errors import PyloxParseError

from pylox.expr import Binary, Expr, Literal
from pylox.stmt import ExprStmt
from pylox.parser import Parser
from pylox.token import Token, TokenType


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            "1 + 2;",
            [
                ExprStmt(
                    Binary(
                        Literal(1),
                        Token(TokenType.PLUS, "+", None, 1),
                        Literal(2),
                    ),
                )
            ],
        ),
    ],
)
def test_parser(source: str, expected: Expr) -> None:
    actual = Parser.from_source(source).parse()
    assert actual is not None
    assert actual == expected


@pytest.mark.parametrize(
    "source",
    [
        # Invalid assignment
        ("var 1 + 2 = 3;"),
    ],
)
def test_parser_raises_errors(source: str) -> None:
    """Check that the parser raises an error on invalid code."""
    parser = Parser.from_source(source)
    with pytest.raises(PyloxParseError):
        parser.parse()
