import enum
import typing as t

import attrs


class TokenTypeType(enum.Enum):
    """The type of a token type."""

    SINGLE_CHARACTER = "single_character"
    MAYBE_MULTI_CHARACTER = "maybe_multi_character"
    KEYWORD = "keyword"
    OTHER = "other"


class TokenType(enum.Enum):
    """A token type in Lox code."""

    # Single-character tokens.
    LEFT_PAREN = ("(", TokenTypeType.SINGLE_CHARACTER)
    RIGHT_PAREN = (")", TokenTypeType.SINGLE_CHARACTER)
    LEFT_BRACE = ("{", TokenTypeType.SINGLE_CHARACTER)
    RIGHT_BRACE = ("}", TokenTypeType.SINGLE_CHARACTER)
    COMMA = (",", TokenTypeType.SINGLE_CHARACTER)
    DOT = (".", TokenTypeType.SINGLE_CHARACTER)
    MINUS = ("-", TokenTypeType.SINGLE_CHARACTER)
    PLUS = ("+", TokenTypeType.SINGLE_CHARACTER)
    SEMICOLON = (";", TokenTypeType.SINGLE_CHARACTER)
    SLASH = ("/", TokenTypeType.SINGLE_CHARACTER)
    STAR = ("*", TokenTypeType.SINGLE_CHARACTER)
    # One or two character tokens
    BANG = ("!", TokenTypeType.MAYBE_MULTI_CHARACTER)
    BANG_EQUAL = ("!=", TokenTypeType.MAYBE_MULTI_CHARACTER)
    EQUAL = ("=", TokenTypeType.MAYBE_MULTI_CHARACTER)
    EQUAL_EQUAL = ("==", TokenTypeType.MAYBE_MULTI_CHARACTER)
    GREATER = (">", TokenTypeType.MAYBE_MULTI_CHARACTER)
    GREATER_EQUAL = (">=", TokenTypeType.MAYBE_MULTI_CHARACTER)
    LESS = ("<", TokenTypeType.MAYBE_MULTI_CHARACTER)
    LESS_EQUAL = ("<=", TokenTypeType.MAYBE_MULTI_CHARACTER)
    IDENTIFIER = ("identifier", TokenTypeType.SINGLE_CHARACTER)
    STRING = ("string", TokenTypeType.SINGLE_CHARACTER)
    NUMBER = ("number", TokenTypeType.SINGLE_CHARACTER)
    # Keywords
    AND = ("and", TokenTypeType.KEYWORD)
    CLASS = ("class", TokenTypeType.KEYWORD)
    ELSE = ("else", TokenTypeType.KEYWORD)
    FALSE = ("false", TokenTypeType.KEYWORD)
    FUN = ("fun", TokenTypeType.KEYWORD)
    FOR = ("for", TokenTypeType.KEYWORD)
    IF = ("if", TokenTypeType.KEYWORD)
    NIL = ("nil", TokenTypeType.KEYWORD)
    OR = ("or", TokenTypeType.KEYWORD)
    PRINT = ("print", TokenTypeType.KEYWORD)
    RETURN = ("return", TokenTypeType.KEYWORD)
    SUPER = ("super", TokenTypeType.KEYWORD)
    THIS = ("this", TokenTypeType.KEYWORD)
    TRUE = ("true", TokenTypeType.KEYWORD)
    VAR = ("var", TokenTypeType.KEYWORD)
    WHILE = ("while", TokenTypeType.KEYWORD)

    COMMENT = ("comment", TokenTypeType.OTHER)
    EOF = ("eof", TokenTypeType.OTHER)

    @classmethod
    def from_keyword(cls, keyword: str) -> "TokenType":
        """Return the TokenType for a keyword."""
        return cls((keyword, TokenTypeType.KEYWORD))


@attrs.define(frozen=True)
class Token:
    """A token in Lox code."""

    token_type: TokenType
    lexeme: str
    literal: t.Any | None
    line: int = attrs.field(repr=False, eq=False)
