import abc
import typing as t

import attrs

from pylox.nodes.base import Node
from pylox.nodes.expr import Expr, VarExpr
from pylox.token import Token


@attrs.define(frozen=True)
class Stmt(Node):
    pass


@attrs.define(frozen=True)
class BlockStmt(Stmt):
    """Represents a block of statements.

    For example:
    ```lox
    {
        print "Hello, world!";
    }
    ```
    """

    statements: t.Sequence[Stmt]

    @property
    def literal(self) -> str:
        return "\n; ".join([stmt.literal for stmt in self.statements])


@attrs.define(frozen=True)
class ClassStmt(Stmt):
    """Represents a class declaration.

    For example:
    ```lox
    class Foo {
        fun bar() {
            print "Hello, world!";
        }
    }
    ```
    """

    name: Token
    methods: list["FunStmt"]
    superclass: VarExpr | None

    @property
    def literal(self) -> str:
        return self.name.lexeme


@attrs.define(frozen=True)
class ExprStmt(Stmt):
    """Represents an expression statement.

    For example:
    ```lox
    clock();
    1 + 2;
    ```
    """

    expr: Expr

    @property
    def literal(self) -> str:
        return self.expr.literal


@attrs.define(frozen=True)
class ForStmt(Stmt):
    """Represents a for loop.

    For example:
    ```lox
    for (var i = 0; i < 10; i = i + 1) {
        print i;
    }
    ```
    ```lox
    for (; i < 10; i = i + 1) {
        print i;
    }
    ```
    ```lox
    for (var i = 0; ; i = i + 1) {
        print i;
    }
    ```
    ```lox
    for (var i = 0; i < 10; ) {
        print i;
    }
    ```
    """

    initializer: Stmt | None
    condition: Expr | None
    increment: Expr | None
    body: Stmt

    @property
    def literal(self) -> str:
        result = "for ("
        result += self.initializer.literal if self.initializer else ""
        result += "; "
        result += self.condition.literal if self.condition else ""
        result += "; "
        result += self.increment.literal if self.increment else ""
        result += ") "
        result += self.body.literal
        return result


@attrs.define(frozen=True)
class FunStmt(Stmt):
    """Represents a function declaration.

    For example:
    ```lox
    fun hello() {
        print "Hello, world!";
    }
    ```
    """

    name: Token
    params: list[Token]
    body: BlockStmt

    @property
    def literal(self) -> str:
        return self.name.lexeme


@attrs.define(frozen=True)
class IfStmt(Stmt):
    """Represents an if statement.

    For example:
    ```lox
    if (true) {
        print "Hello, world!";
    }
    ```
    """

    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    @property
    def literal(self) -> str:
        return self.condition.literal


@attrs.define(frozen=True)
class PrintStmt(Stmt):
    """Represents a print statement.

    For example:
    ```lox
    print "Hello, world!";
    ```
    """

    expr: Expr

    @property
    def literal(self) -> str:
        return self.expr.literal


@attrs.define(frozen=True)
class ReturnStmt(Stmt):
    """Represents a return statement.

    For example:
    ```lox
    return 1;
    ```
    """

    keyword: Token
    value: Expr | None

    @property
    def literal(self) -> str:
        value = self.value.literal if self.value else ""
        return f"return {value}"


@attrs.define(frozen=True)
class VarStmt(Stmt):
    """Represents a variable declaration statement.

    For example:
    ```lox
    var a = 1;
    ```
    """

    name: Token
    initializer: Expr | None

    @property
    def literal(self) -> str:
        return self.name.lexeme


@attrs.define(frozen=True)
class WhileStmt(Stmt):
    """Represents a while loop.

    For example:
    ```lox
    while (true) {
        print "Hello, world!";
    }
    ```
    """

    condition: Expr
    body: Stmt

    @property
    def literal(self) -> str:
        return f"while {self.condition.literal} {self.body.literal}"


R = t.TypeVar("R")


class StmtVisitor(abc.ABC, t.Generic[R]):
    @abc.abstractmethod
    def visit_block_stmt(self, stmt: BlockStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_class_stmt(self, stmt: ClassStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_expr_stmt(self, stmt: ExprStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_for_stmt(self, stmt: ForStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_fun_stmt(self, stmt: FunStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_if_stmt(self, stmt: IfStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_print_stmt(self, stmt: PrintStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_return_stmt(self, stmt: ReturnStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_var_stmt(self, stmt: VarStmt) -> R:
        ...

    @abc.abstractmethod
    def visit_while_stmt(self, stmt: WhileStmt) -> R:
        ...


def visit_statement(stmt: Stmt, visitor: StmtVisitor[R]) -> R:
    """Visits a statement using the given visitor.

    This is a helper function that is used in place of the traditional visitor pattern.
    See `pylox.nodes.expr.visit_expression` for more details.
    """
    mapping = {
        BlockStmt.__qualname__: visitor.visit_block_stmt,
        ClassStmt.__qualname__: visitor.visit_class_stmt,
        ExprStmt.__qualname__: visitor.visit_expr_stmt,
        ForStmt.__qualname__: visitor.visit_for_stmt,
        FunStmt.__qualname__: visitor.visit_fun_stmt,
        IfStmt.__qualname__: visitor.visit_if_stmt,
        PrintStmt.__qualname__: visitor.visit_print_stmt,
        ReturnStmt.__qualname__: visitor.visit_return_stmt,
        VarStmt.__qualname__: visitor.visit_var_stmt,
        WhileStmt.__qualname__: visitor.visit_while_stmt,
    }
    return mapping[stmt.__class__.__qualname__](t.cast(t.Any, stmt))
