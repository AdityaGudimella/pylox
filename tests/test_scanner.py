import pytest

from pylox.scanner import Scanner
from pylox.token import Token, TokenType


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            # Empty source
            "",
            [Token(TokenType.EOF, "", None, 1)],
        ),
        (
            # Single character tokens
            "=+(){},;",
            [
                Token(TokenType.EQUAL, "=", None, 1),
                Token(TokenType.PLUS, "+", None, 1),
                Token(TokenType.LEFT_PAREN, "(", None, 1),
                Token(TokenType.RIGHT_PAREN, ")", None, 1),
                Token(TokenType.LEFT_BRACE, "{", None, 1),
                Token(TokenType.RIGHT_BRACE, "}", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.SEMICOLON, ";", None, 1),
                Token(TokenType.EOF, "", None, 1),
            ],
        ),
        (
            # White space
            " ",
            [Token(TokenType.EOF, "", None, 1)],
        ),
        (
            # One or two character tokens
            ">=,<=,==,!=,!,<,>,=,/",
            [
                Token(TokenType.GREATER_EQUAL, ">=", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.LESS_EQUAL, "<=", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.EQUAL_EQUAL, "==", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.BANG_EQUAL, "!=", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.BANG, "!", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.LESS, "<", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.GREATER, ">", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.EQUAL, "=", None, 1),
                Token(TokenType.COMMA, ",", None, 1),
                Token(TokenType.SLASH, "/", None, 1),
                Token(TokenType.EOF, "", None, 1),
            ],
        ),
        (
            """
            // This is a comment

            """,
            [
                Token(TokenType.COMMENT, "// This is a comment", None, 2),
                Token(TokenType.EOF, "", None, 3),
            ],
        ),
        (
            "// This is a comment",
            [
                Token(TokenType.COMMENT, "// This is a comment", None, 1),
                Token(TokenType.EOF, "", None, 2),
            ],
        ),
        (
            """
            var five = 5;
            """,
            [
                Token(TokenType.VAR, "var", None, 2),
                Token(TokenType.IDENTIFIER, "five", None, 2),
                Token(TokenType.EQUAL, "=", None, 2),
                Token(TokenType.NUMBER, "5", 5, 2),
                Token(TokenType.SEMICOLON, ";", None, 2),
                Token(TokenType.EOF, "", None, 3),
            ],
        ),
        (
            "var a = nil;",
            [
                Token(TokenType.VAR, "var", None, 1),
                Token(TokenType.IDENTIFIER, "a", None, 1),
                Token(TokenType.EQUAL, "=", None, 1),
                Token(TokenType.NIL, "nil", None, 1),
                Token(TokenType.SEMICOLON, ";", None, 1),
                Token(TokenType.EOF, "", None, 1),
            ],
        ),
        (
            # Strings
            """
            var a = "hello";
            """,
            [
                Token(TokenType.VAR, "var", None, 2),
                Token(TokenType.IDENTIFIER, "a", None, 2),
                Token(TokenType.EQUAL, "=", None, 2),
                Token(TokenType.STRING, '"hello"', "hello", 2),
                Token(TokenType.SEMICOLON, ";", None, 2),
                Token(TokenType.EOF, "", None, 3),
            ],
        ),
        (
            """
            var five = 5;
            var ten = 10;

            fun add(a, b) {
                return a + b;
            }

            var result = add(five, ten);
            """,
            [
                Token(TokenType.VAR, "var", None, 2),
                Token(TokenType.IDENTIFIER, "five", None, 2),
                Token(TokenType.EQUAL, "=", None, 2),
                Token(TokenType.NUMBER, "5", 5, 2),
                Token(TokenType.SEMICOLON, ";", None, 2),
                Token(TokenType.VAR, "var", None, 3),
                Token(TokenType.IDENTIFIER, "ten", None, 3),
                Token(TokenType.EQUAL, "=", None, 3),
                Token(TokenType.NUMBER, "10", 10, 3),
                Token(TokenType.SEMICOLON, ";", None, 3),
                Token(TokenType.FUN, "fun", None, 5),
                Token(TokenType.IDENTIFIER, "add", None, 5),
                Token(TokenType.LEFT_PAREN, "(", None, 5),
                Token(TokenType.IDENTIFIER, "a", None, 5),
                Token(TokenType.COMMA, ",", None, 5),
                Token(TokenType.IDENTIFIER, "b", None, 5),
                Token(TokenType.RIGHT_PAREN, ")", None, 5),
                Token(TokenType.LEFT_BRACE, "{", None, 5),
                Token(TokenType.RETURN, "return", None, 6),
                Token(TokenType.IDENTIFIER, "a", None, 6),
                Token(TokenType.PLUS, "+", None, 6),
                Token(TokenType.IDENTIFIER, "b", None, 6),
                Token(TokenType.SEMICOLON, ";", None, 6),
                Token(TokenType.RIGHT_BRACE, "}", None, 7),
                Token(TokenType.VAR, "var", None, 9),
                Token(TokenType.IDENTIFIER, "result", None, 9),
                Token(TokenType.EQUAL, "=", None, 9),
                Token(TokenType.IDENTIFIER, "add", None, 9),
                Token(TokenType.LEFT_PAREN, "(", None, 9),
                Token(TokenType.IDENTIFIER, "five", None, 9),
                Token(TokenType.COMMA, ",", None, 9),
                Token(TokenType.IDENTIFIER, "ten", None, 9),
                Token(TokenType.RIGHT_PAREN, ")", None, 9),
                Token(TokenType.SEMICOLON, ";", None, 9),
                Token(TokenType.EOF, "", None, 10),
            ],
        ),
        (
            """
            if (a < b) {
                return true;
            } else {
                return false;
            }
            """,
            [
                Token(TokenType.IF, "if", None, 2),
                Token(TokenType.LEFT_PAREN, "(", None, 2),
                Token(TokenType.IDENTIFIER, "a", None, 2),
                Token(TokenType.LESS, "<", None, 2),
                Token(TokenType.IDENTIFIER, "b", None, 2),
                Token(TokenType.RIGHT_PAREN, ")", None, 2),
                Token(TokenType.LEFT_BRACE, "{", None, 2),
                Token(TokenType.RETURN, "return", None, 3),
                Token(TokenType.TRUE, "true", None, 3),
                Token(TokenType.SEMICOLON, ";", None, 3),
                Token(TokenType.RIGHT_BRACE, "}", None, 4),
                Token(TokenType.ELSE, "else", None, 5),
                Token(TokenType.LEFT_BRACE, "{", None, 5),
                Token(TokenType.RETURN, "return", None, 6),
                Token(TokenType.FALSE, "false", None, 6),
                Token(TokenType.SEMICOLON, ";", None, 6),
                Token(TokenType.RIGHT_BRACE, "}", None, 7),
                Token(TokenType.EOF, "", None, 8),
            ],
        ),
    ],
)
def test_next_token(source: str, expected: list[Token]):
    """Test that the Scanner can extract Tokens from source code."""
    scanner = Scanner.from_source(source)
    actual = scanner.scan_tokens()
    assert actual == expected


@pytest.mark.skip(reason="Not implemented yet.")
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
def test_scanner(source: str, expected: list[Token]) -> None:
    actual = Scanner.from_source(source).scan_tokens()
    assert actual == expected
