import attrs

from pylox.errors import PyloxScanError
from pylox.token import Token, TokenType


class WhiteSpaceError(Exception):
    """An error raised when whitespace is found in an unexpected place."""


@attrs.define()
class Source:
    """Source code to be scanned."""

    text: str

    _current_position: int = attrs.field(init=False, default=0)
    _lines_seen: int = attrs.field(init=False, default=0)

    @property
    def line(self) -> int:
        """Return the current line number."""
        return self._lines_seen + 1

    @property
    def current_position(self) -> int:
        """Return the current position in the source code."""
        return self._current_position

    @property
    def current_char(self) -> str:
        """Return the current character in the source code."""
        return self.text[self._current_position]

    @property
    def is_at_end(self) -> bool:
        """Return True if the scanner is at the end of the source code."""
        return self._current_position >= len(self.text)

    def check_next(self, char: str) -> bool:
        """Return True if the next character in the source code is the given character."""
        return (
            False
            if any(
                (
                    self._current_position >= len(self.text),
                    self._current_position + 1 >= len(self.text),
                )
            )
            else self.peek() == char
        )

    def peek(self) -> str:
        """Return the next character in the source code."""
        return self.text[self._current_position + 1]

    def advance(self, n: int = 1) -> None:
        """Advance to the next character in the source code."""
        for _ in range(n):
            if self.current_char == "\n":
                self._lines_seen += 1
            self._current_position += 1

    def __getitem__(self, item: int | slice) -> str:
        """Return the character at the given index."""
        return self.text[item]


@attrs.define()
class Scanner:
    """A Scanner extracts Tokens from source code."""

    source: Source

    @classmethod
    def from_source(cls, source: str) -> "Scanner":
        """Create a Scanner from source code."""
        return cls(Source(source))

    def _extract_token_and_advance(self) -> Token:
        """Return the next Token in the source code."""
        match self.source.current_char:
            case "(":
                self.source.advance()
                return Token(TokenType.LEFT_PAREN, "(", None, self.source.line)
            case ")":
                self.source.advance()
                return Token(TokenType.RIGHT_PAREN, ")", None, self.source.line)
            case "{":
                self.source.advance()
                return Token(TokenType.LEFT_BRACE, "{", None, self.source.line)
            case "}":
                self.source.advance()
                return Token(TokenType.RIGHT_BRACE, "}", None, self.source.line)
            case ",":
                self.source.advance()
                return Token(TokenType.COMMA, ",", None, self.source.line)
            case ".":
                self.source.advance()
                return Token(TokenType.DOT, ".", None, self.source.line)
            case "-":
                self.source.advance()
                return Token(TokenType.MINUS, "-", None, self.source.line)
            case "+":
                self.source.advance()
                return Token(TokenType.PLUS, "+", None, self.source.line)
            case ";":
                self.source.advance()
                return Token(TokenType.SEMICOLON, ";", None, self.source.line)
            case "*":
                self.source.advance()
                return Token(TokenType.STAR, "*", None, self.source.line)
            case "!":
                if self.source.check_next("="):
                    self.source.advance()
                    self.source.advance()
                    return Token(TokenType.BANG_EQUAL, "!=", None, self.source.line)
                else:
                    self.source.advance()
                    return Token(TokenType.BANG, "!", None, self.source.line)
            case "=":
                if self.source.check_next("="):
                    self.source.advance()
                    self.source.advance()
                    return Token(TokenType.EQUAL_EQUAL, "==", None, self.source.line)
                else:
                    self.source.advance()
                    return Token(TokenType.EQUAL, "=", None, self.source.line)
            case "<":
                if self.source.check_next("="):
                    self.source.advance(n=2)
                    return Token(TokenType.LESS_EQUAL, "<=", None, self.source.line)
                else:
                    self.source.advance()
                    return Token(TokenType.LESS, "<", None, self.source.line)
            case ">":
                if self.source.check_next("="):
                    self.source.advance(n=2)
                    return Token(TokenType.GREATER_EQUAL, ">=", None, self.source.line)
                else:
                    self.source.advance()
                    return Token(TokenType.GREATER, ">", None, self.source.line)
            case "/":
                if self.source.check_next("/"):
                    return self._comment()
                self.source.advance()
                return Token(TokenType.SLASH, "/", None, self.source.line)
            case c if c.isspace():
                while self.source.current_char.isspace():
                    self.source.advance()
                raise WhiteSpaceError()
            case '"':
                return self._string()
            case c if c.isnumeric():
                return self._number()
            case c if c.isalpha() or c == "_":
                # A variable name can start with a letter or underscore.
                return self._identifier()
            case _:
                raise PyloxScanError(
                    f"Unexpected character: {self.source.current_char}",
                    self.source.line,
                )
        raise RuntimeError(f"No token returned for char: {self.source.current_char}")

    def _comment(self) -> Token:
        """Return a comment Token.

        Assumes that the current character is a slash and the previous one is a slash.
        """
        start = self.source.current_position
        while not (self.source.is_at_end or self.source.check_next("\n")):
            self.source.advance()
        if not self.source.is_at_end:
            self.source.advance()
        text = self.source[start : self.source.current_position]
        return Token(TokenType.COMMENT, text, None, self.source.line)

    def _string(self) -> Token:
        """Return a string Token.

        Assumes that the current character is a double quote.
        """
        start = self.source.current_position
        while not (self.source.is_at_end or self.source.check_next('"')):
            self.source.advance()
        if self.source.is_at_end:
            raise PyloxScanError("Unterminated string.", self.source.line)
        self.source.advance(n=2)
        text = self.source[start : self.source.current_position]
        return Token(TokenType.STRING, text, text[1:-1], self.source.line)

    def _number(self) -> Token:
        """Return a number Token."""
        start = self.source.current_position
        while self.source.current_char.isnumeric():
            self.source.advance()
        if self.source.current_char == "." and self.source.peek().isnumeric():
            self.source.advance()
            while self.source.current_char.isnumeric():
                self.source.advance()
        text = self.source[start : self.source.current_position]
        return Token(TokenType.NUMBER, text, float(text), self.source.line)

    def _identifier(self) -> Token:
        """Return an identifier Token."""
        start = self.source.current_position
        while self.source.current_char.isalnum() or self.source.current_char == "_":
            # An identifier can contain letters, numbers, or underscores.
            self.source.advance()
        text = self.source[start : self.source.current_position]
        try:
            token_type = TokenType.from_keyword(text)
        except ValueError:
            token_type = TokenType.IDENTIFIER
        return Token(
            token_type,
            text,
            None,
            self.source.line,
        )

    def scan_tokens(self) -> list[Token]:
        """Scan the source code and return a list of Tokens."""
        tokens: list[Token] = []
        while True:
            try:
                tokens.append(self._extract_token_and_advance())
            except IndexError:
                tokens.append(Token(TokenType.EOF, "", None, self.source.line))
                break
            except WhiteSpaceError:
                pass
        return tokens
