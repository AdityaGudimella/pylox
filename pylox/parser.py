import typing as t

import attrs

from pylox import nodes as pn
from pylox.constants import FunctionType
from pylox.errors import Errors, PyloxParseError
from pylox.scanner import Scanner
from pylox.token import Token, TokenType


@attrs.define()
class Tokens:
    """A Tokens is a sequence of Tokens."""

    tokens: t.Sequence[Token]
    errors: Errors

    _current_position: int = attrs.field(init=False, default=0)

    @classmethod
    def from_source(
        cls, source: str, errors: Errors, filter_comments: bool = True
    ) -> "Tokens":
        """Create a Tokens from source code."""
        tokens = Scanner.from_source(source).scan_tokens()
        if filter_comments:
            tokens = list(
                filter(lambda token: token.token_type != TokenType.COMMENT, tokens)
            )
        return cls(tokens=tokens, errors=errors)

    @property
    def current_position(self) -> int:
        """Return the current position in the tokens."""
        return self._current_position

    @property
    def previous_token(self) -> Token:
        """Return the previous token."""
        if self._current_position == 0:
            raise RuntimeError(
                "Cannot get previous token at the beginning of the tokens."
            )
        return self.tokens[self._current_position - 1]

    @property
    def current_token(self) -> Token:
        """Return the current token."""
        return self.tokens[self._current_position]

    @property
    def is_at_end(self) -> bool:
        """Return True if the parser is at the end of the tokens."""
        try:
            return self.current_token.token_type == TokenType.EOF
        except IndexError:
            return True

    def advance(self) -> None:
        """Advance to the next token."""
        self._current_position += 1

    def check_token_type(self, token_type: TokenType) -> bool:
        """Return True if the next token is of the given type."""
        return False if self.is_at_end else self.current_token.token_type == token_type

    def advance_if_match(self, *token_types: TokenType) -> bool:
        """Advance to the next token if it is any of the given type."""
        for token_type in token_types:
            if self.check_token_type(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume the next token if it is of the given type else, raise error."""
        if self.check_token_type(token_type):
            self.advance()
            return self.previous_token
        raise self.errors.record(
            PyloxParseError.from_token(token=self.current_token, message=message)
        )

    def __rich__(self) -> str:
        return "\n".join(map(str, self.tokens))


@attrs.define()
class Parser:
    """A Parser extracts an AST from a sequence of Tokens.

    The Parser follows the following grammar:

    program        -> declaration* EOF ;
    # Declarations
    declaration    -> classDecl
                    | funDecl
                    | varDecl
                    | statement ;

    classDecl      -> "class" IDENTIFIER ( "<" IDENTIFIER )?
                    "{" function* "}" ;
    funDecl        -> "fun" function ;
    varDecl        -> "var" IDENTIFIER ( "=" expression )? ";" ;
    # Statements
    statement      -> exprStmt
                    | forStmt
                    | ifStmt
                    | printStmt
                    | returnStmt
                    | whileStmt
                    | block ;
    exprStmt       -> expression ";" ;
    forStmt        -> "for" "(" ( varDecl | exprStmt | ";" )
                    expression? ";" expression? ")" statement ;
    ifStmt         -> "if" "(" expression ")" statement
                    ( "else" statement )? ;
    printStmt      -> "print" expression ";" ;
    returnStmt     -> "return" expression? ";" ;
    whileStmt      -> "while" "(" expression ")" statement ;
    block          -> "{" declaration* "}" ;
    # Expressions
    expression     -> assignment ;
    assignment     -> ( call "." )? IDENTIFIER "=" assignment
                    | logic_or ;
    logic_or       -> logic_and ( "or" logic_and )* ;
    logic_and      -> equality ( "and" equality )* ;
    equality       -> comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term           -> factor ( ( "-" | "+" ) factor )* ;
    factor         -> unary ( ( "/" | "*" ) unary )* ;
    unary          -> ( "!" | "-" ) unary | call ;
    call           -> primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
    primary        -> "true" | "false" | "nil" | "this" | NUMBER | STRING
                    | IDENTIFIER | "(" expression ")"
                    | "super" "." IDENTIFIER ;
    # Utility rules
    function      -> IDENTIFIER "(" parameters? ")" block ;
    parameters    -> IDENTIFIER ( "," IDENTIFIER )* ;
    arguments     -> expression ( "," expression )* ;
    # Lexical rules
    NUMBER        -> DIGIT+ ( "." DIGIT+ )? ;
    STRING        -> '"' ( ESCAPE | ~'"' )* '"' ;
    IDENTIFIER    -> ALPHA ( ALPHA | DIGIT )* ;
    ALPHA         -> [a-zA-Z_] ;
    DIGIT         -> [0-9] ;
    """

    tokens: Tokens

    errors: Errors = attrs.field(factory=Errors)

    @classmethod
    def from_source(cls, source: str, errors: Errors) -> "Parser":
        """Create a Parser from source code."""
        return cls(tokens=Tokens.from_source(source, errors=errors), errors=errors)

    def parse(self) -> list[pn.Stmt]:
        """Return an AST from a sequence of Tokens."""
        statements: list[pn.Stmt] = []
        while not self.tokens.is_at_end:
            statements.append(self.parse_declaration())
        return statements

    def parse_declaration(self) -> pn.Stmt:
        """Parse a declaration."""
        try:
            if self.tokens.advance_if_match(TokenType.CLASS):
                return self.parse_class()
            if self.tokens.advance_if_match(TokenType.FUN):
                return self.parse_function(FunctionType.FUNCTION)
            if self.tokens.advance_if_match(TokenType.VAR):
                return self.parse_var()
            return self.parse_statement()
        except PyloxParseError as err:
            self.errors.record(err)
            self.synchronize()
            raise

    def parse_class(self) -> pn.Stmt:
        """Parse a class.

        Parses rule:
            classDecl      -> "class" IDENTIFIER ( "<" IDENTIFIER )?
                            "{" function* "}" ;
        """
        name = self.tokens.consume(TokenType.IDENTIFIER, "Expect class name.")
        if self.tokens.advance_if_match(TokenType.LESS):
            superclass = pn.VarExpr(
                self.tokens.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            )
        else:
            superclass = None
        self.tokens.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods: list[pn.FunStmt] = []
        while (
            not self.tokens.check_token_type(TokenType.RIGHT_BRACE)
            and not self.tokens.is_at_end
        ):
            method = self.parse_function(FunctionType.METHOD)
            assert isinstance(method, pn.FunStmt)
            methods.append(method)
        self.tokens.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return pn.ClassStmt(name=name, superclass=superclass, methods=methods)

    def parse_function(self, function_type: FunctionType) -> pn.Stmt:
        """Parse a function."""
        kind = function_type.value
        name = self.tokens.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.tokens.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: list[Token] = []
        if not self.tokens.check_token_type(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.errors.record(
                        PyloxParseError.from_token(
                            token=self.tokens.current_token,
                            message="Cannot have more than 255 parameters.",
                        )
                    )
                parameters.append(
                    self.tokens.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self.tokens.advance_if_match(TokenType.COMMA):
                    break
        self.tokens.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.tokens.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.parse_block()
        return pn.FunStmt(
            name=name,
            params=parameters,
            body=pn.BlockStmt(body),
        )

    def parse_var(self) -> pn.Stmt:
        """Parse a var."""
        name = self.tokens.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = (
            self.parse_expression()
            if self.tokens.advance_if_match(TokenType.EQUAL)
            else None
        )
        self.tokens.consume(
            TokenType.SEMICOLON, "Expect ';' after variable declaration."
        )
        return pn.VarStmt(name=name, initializer=initializer)

    def parse_statement(self) -> pn.Stmt:
        """Parse a statement."""
        if self.tokens.advance_if_match(TokenType.FOR):
            return self.parse_for()
        if self.tokens.advance_if_match(TokenType.IF):
            return self.parse_if()
        if self.tokens.advance_if_match(TokenType.PRINT):
            return self.parse_print()
        if self.tokens.advance_if_match(TokenType.RETURN):
            return self.parse_return()
        if self.tokens.advance_if_match(TokenType.WHILE):
            return self.parse_while()
        if self.tokens.advance_if_match(TokenType.LEFT_BRACE):
            return pn.BlockStmt(self.parse_block())
        return self.parse_expression_statement()

    def parse_for(self) -> pn.Stmt:
        """Parse a for."""
        self.tokens.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.tokens.advance_if_match(TokenType.SEMICOLON):
            initializer = None
        elif self.tokens.advance_if_match(TokenType.VAR):
            initializer = self.parse_var()
        else:
            initializer = self.parse_expression_statement()
        condition = (
            None
            if self.tokens.check_token_type(TokenType.SEMICOLON)
            else self.parse_expression()
        )
        self.tokens.consume(TokenType.SEMICOLON, "Expect ';' after for condition.")
        increment = (
            None
            if self.tokens.check_token_type(TokenType.RIGHT_PAREN)
            else self.parse_expression()
        )
        self.tokens.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.parse_statement()
        return pn.ForStmt(
            initializer=initializer,
            condition=condition,
            increment=increment,
            body=body,
        )

    def parse_if(self) -> pn.Stmt:
        """Parse an if."""
        self.tokens.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.parse_expression()
        self.tokens.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.parse_statement()
        else_branch = (
            self.parse_statement()
            if self.tokens.advance_if_match(TokenType.ELSE)
            else None
        )
        return pn.IfStmt(
            condition=condition, then_branch=then_branch, else_branch=else_branch
        )

    def parse_print(self) -> pn.Stmt:
        """Parse a print."""
        expr = self.parse_expression()
        self.tokens.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return pn.PrintStmt(expr)

    def parse_return(self) -> pn.Stmt:
        """Parse a return."""
        keyword = self.tokens.previous_token
        value = (
            None
            if self.tokens.check_token_type(TokenType.SEMICOLON)
            else self.parse_expression()
        )
        self.tokens.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return pn.ReturnStmt(keyword=keyword, value=value)

    def parse_while(self) -> pn.Stmt:
        """Parse a while."""
        self.tokens.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.parse_expression()
        self.tokens.consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body = self.parse_statement()
        return pn.WhileStmt(condition=condition, body=body)

    def parse_block(self) -> list[pn.Stmt]:
        """Parse a block."""
        result: list[pn.Stmt] = []
        while (
            not self.tokens.check_token_type(TokenType.RIGHT_BRACE)
            and not self.tokens.is_at_end
        ):
            result.append(self.parse_declaration())
        self.tokens.consume(
            TokenType.RIGHT_BRACE,
            f"Expect '}}' after block on token: {self.tokens.current_token.lexeme}.",
        )
        return result

    def parse_expression_statement(self) -> pn.Stmt:
        """Parse an expression statement."""
        expr = self.parse_expression()
        self.tokens.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return pn.ExprStmt(expr)

    def parse_expression(self) -> pn.Expr:
        """Parse an expression."""
        return self.parse_assignment()

    def parse_assignment(self) -> pn.Expr:
        """Parse an assignment."""
        expr = self.parse_or()
        if self.tokens.advance_if_match(TokenType.EQUAL):
            equals = self.tokens.previous_token
            value = self.parse_assignment()

            # sourcery skip: remove-unnecessary-else, swap-if-else-branches
            if isinstance(expr, pn.VarExpr):
                name = expr.name
                return pn.AssignExpr(name, value)
            elif isinstance(expr, pn.GetExpr):
                return pn.SetExpr(expr.obj, expr.name, value)
            else:
                raise self.errors.record(
                    PyloxParseError.from_token(
                        token=equals, message="Invalid assignment target."
                    )
                )
        return expr

    def parse_or(self) -> pn.Expr:
        """Parse an or."""
        expr = self.parse_and()

        while self.tokens.advance_if_match(TokenType.OR):
            operator = self.tokens.previous_token
            right = self.parse_and()
            expr = pn.LogicalExpr(expr, operator, right)

        return expr

    def parse_and(self) -> pn.Expr:
        """Parse an and."""
        expr = self.parse_equality()

        while self.tokens.advance_if_match(TokenType.AND):
            operator = self.tokens.previous_token
            right = self.parse_equality()
            expr = pn.LogicalExpr(expr, operator, right)

        return expr

    def parse_equality(self) -> pn.Expr:
        """Parse an equality."""
        expr = self.parse_comparison()

        while self.tokens.advance_if_match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.tokens.previous_token
            right = self.parse_comparison()
            expr = pn.BinaryExpr(expr, operator, right)

        return expr

    def parse_comparison(self) -> pn.Expr:
        """Parse a comparison."""
        expr = self.parse_term()

        while self.tokens.advance_if_match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.tokens.previous_token
            right = self.parse_term()
            expr = pn.BinaryExpr(expr, operator, right)

        return expr

    def parse_term(self) -> pn.Expr:
        """Parse a term."""
        expr = self.parse_factor()

        while self.tokens.advance_if_match(TokenType.MINUS, TokenType.PLUS):
            operator = self.tokens.previous_token
            right = self.parse_factor()
            expr = pn.BinaryExpr(expr, operator, right)

        return expr

    def parse_factor(self) -> pn.Expr:
        """Parse a factor."""
        expr = self.parse_unary()

        while self.tokens.advance_if_match(TokenType.SLASH, TokenType.STAR):
            operator = self.tokens.previous_token
            right = self.parse_unary()
            expr = pn.BinaryExpr(expr, operator, right)

        return expr

    def parse_unary(self) -> pn.Expr:
        """Parse a unary."""
        if self.tokens.advance_if_match(TokenType.BANG, TokenType.MINUS):
            operator = self.tokens.previous_token
            right = self.parse_unary()
            return pn.UnaryExpr(operator, right)

        return self.parse_call()

    def parse_call(self) -> pn.Expr:
        """Parse a call.

        Parses rule: call → primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
        Examples:
        1. `a()` -> `a` is the primary, `()` is the ( arguments | IDENTIFIER )* part
        2. `a(2)` -> `a` is the primary, `(2)` is the ( arguments | IDENTIFIER )* part
        3. `a.b` -> `a` is the primary, `.b` is the ( arguments | IDENTIFIER )* part
        """
        # matches: primary
        expr = self.parse_primary()

        while True:
            # mactches: ( "(" arguments? ")" | "." IDENTIFIER )*
            if self.tokens.advance_if_match(TokenType.LEFT_PAREN):
                # matches: "(" arguments? ")"
                expr = self.finish_call(expr)
            elif self.tokens.advance_if_match(TokenType.DOT):
                # matches: "." IDENTIFIER
                name = self.tokens.consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                expr = pn.GetExpr(expr, name)
            else:
                break

        return expr

    def parse_primary(self) -> pn.Expr:
        """Parse a primary."""
        if self.tokens.advance_if_match(TokenType.FALSE):
            return pn.LiteralExpr(False)
        if self.tokens.advance_if_match(TokenType.TRUE):
            return pn.LiteralExpr(True)
        if self.tokens.advance_if_match(TokenType.NIL):
            return pn.LiteralExpr(None)

        if self.tokens.advance_if_match(TokenType.NUMBER, TokenType.STRING):
            return pn.LiteralExpr(self.tokens.previous_token.literal)

        if self.tokens.advance_if_match(TokenType.SUPER):
            keyword = self.tokens.previous_token
            self.tokens.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.tokens.consume(
                TokenType.IDENTIFIER, "Expect superclass method name."
            )
            return pn.SuperExpr(keyword, method)

        if self.tokens.advance_if_match(TokenType.THIS):
            return pn.ThisExpr(self.tokens.previous_token)

        if self.tokens.advance_if_match(TokenType.IDENTIFIER):
            return pn.VarExpr(self.tokens.previous_token)

        if self.tokens.advance_if_match(TokenType.LEFT_PAREN):
            expr = self.parse_expression()
            self.tokens.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return pn.GroupingExpr(expr)

        previous_token = (
            self.tokens.previous_token
            if self.tokens.current_position > 0
            else "<Beginning>"
        )

        raise self.errors.record(
            PyloxParseError.from_token(
                token=self.tokens.current_token,
                message=(
                    f"Expect expression after {previous_token}"
                    + f" on {self.tokens.current_token.lexeme}."
                ),
            )
        )

    def finish_call(self, callee: pn.Expr) -> pn.Expr:
        """Finish a call.

        Parses rule: arguments → expression ( "," expression )* ;
        """
        arguments = []
        while not self.tokens.check_token_type(TokenType.RIGHT_PAREN):
            if len(arguments) >= 255:
                raise self.errors.record(
                    PyloxParseError.from_token(
                        token=self.tokens.current_token,
                        message="Cannot have more than 255 arguments.",
                    )
                )
            arguments.append(self.parse_expression())
            if not self.tokens.advance_if_match(TokenType.COMMA):
                break
        self.tokens.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return pn.CallExpr(callee, arguments)

    def synchronize(self) -> None:
        """Synchronize the parser."""
        self.tokens.advance()
        while not self.tokens.is_at_end:
            if self.tokens.previous_token.token_type == TokenType.SEMICOLON:
                return

            if self.tokens.current_token.token_type in {
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            }:
                return

            self.tokens.advance()
