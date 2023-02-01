import pytest

from pylox import nodes as pn
from pylox.errors import Errors, PyloxParseError
from pylox.parser import Parser
from pylox.token import Token, TokenType
from tests.parser.parser_test_params import TEST_PARSER_PARAMS


@pytest.mark.parametrize(
    "source, method, expected",
    [
        (
            "1;",
            "parse_primary",
            pn.LiteralExpr(value=1.0),
        ),
        (
            "1 + 2;",
            "parse_expression",
            pn.BinaryExpr(
                pn.LiteralExpr(1.0),
                Token(TokenType.PLUS, "+", None, 1),
                pn.LiteralExpr(2.0),
            ),
        ),
    ],
)
def test_parser_methods(source: str, method: str, expected: pn.Expr) -> None:
    """Check that the parser methods return the correct nodes."""
    parser = Parser.from_source(source, errors=Errors())
    actual = getattr(parser, method)()
    assert actual == expected


@pytest.mark.parametrize("source, expected", TEST_PARSER_PARAMS)
def test_parser(source: str, expected: pn.Expr) -> None:
    actual = Parser.from_source(source, errors=Errors()).parse()
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
    parser = Parser.from_source(source, errors=Errors())
    with pytest.raises(PyloxParseError):
        parser.parse()
