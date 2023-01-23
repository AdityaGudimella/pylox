import typing as t

import pytest

from pylox.scanner import Scanner
from pylox.token import Token, TokenType


@pytest.mark.parametrize(
    "source, expected",
    [
        # (
        #     "1 + 2",
        #     [
        #         Token(TokenType.NUMBER, "1", 1, 1),
        #         Token(TokenType.PLUS, "+", None, 1),
        #         Token(TokenType.NUMBER, "2", 2, 1),
        #         Token(TokenType.EOF, "", None, 1),
        #     ],
        # ),
        # Test expression containing boolean literals
        (
            "true",
            [
                Token(TokenType.TRUE, "true", "true", 1),
                Token(TokenType.EOF, "", None, 1),
            ],
        ),
        # Test expression containing boolean literals
        (
            "false",
            [
                Token(TokenType.FALSE, "false", "false", 1),
                Token(TokenType.EOF, "", None, 1),
            ],
        ),
        # Test expression containing nil literal
        (
            "nil",
            [
                Token(TokenType.NIL, "nil", "nil", 1),
                Token(TokenType.EOF, "", None, 1),
            ],
        ),
    ],
)
def test_scanner(source: str, expected: list[Token[t.Any]]) -> None:
    actual = Scanner.from_source(source).scan_tokens()
    assert actual == expected
