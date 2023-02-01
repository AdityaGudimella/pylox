import pytest

from pylox import nodes as pn
from pylox.ast_formatter import ASTFormatter
from pylox.token import Token, TokenType


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            pn.BinaryExpr(
                pn.UnaryExpr(Token(TokenType.MINUS, "-", None, 1), pn.LiteralExpr(123)),
                Token(TokenType.STAR, "*", None, 1),
                pn.GroupingExpr(pn.LiteralExpr(45.67)),
            ),
            "(* (- 123) (group 45.67))",
        )
    ],
)
def test_ast_printer(expr: pn.Node, expected: str) -> None:
    actual = pn.visit_node(expr, ASTFormatter())
    assert actual == expected, actual
