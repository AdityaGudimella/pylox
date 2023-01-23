import pytest

from pylox.ast_formatter import ASTFormatter
from pylox.expr import Binary, Expr, Literal, Unary, Grouping
from pylox.token import Token, TokenType


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            Binary(
                Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
                Token(TokenType.STAR, "*", None, 1),
                Grouping(Literal(45.67)),
            ),
            "(* (- 123) (group 45.67))",
        )
    ],
)
def test_ast_printer(expr: Expr, expected: str) -> None:
    actual = ASTFormatter().format(expr)
    assert actual == expected, actual
