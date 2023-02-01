import abc
import typing as t

import attrs

from pylox.nodes.base import Node
from pylox.token import Token


@attrs.define(frozen=True)
class Expr(Node):
    pass


@attrs.define(frozen=True)
class AssignExpr(Expr):
    """Assign a value to a variable.

    For example:
    ```lox
    a = 1;
    ```
    """

    name: Token
    value: Expr

    @property
    def literal(self) -> str:
        return f"{self.name.lexeme} = {self.value}"


@attrs.define(frozen=True)
class BinaryExpr(Expr):
    """Represents a binary expression.

    Examples:
    ```lox
    a + b;
    1 - 2;
    1.0 * 2.0;
    ```

    NOTE: Expressions like `true or false` are represented as a `LogicalExpr`.
    """

    left: Expr
    operator: Token
    right: Expr

    @property
    def literal(self) -> str:
        return f"{self.left.literal} {self.operator.lexeme} {self.right.literal}"


@attrs.define(frozen=True)
class CallExpr(Expr):
    """Call a function or method.

    For example:
    ```lox
    fun("Hello, world!");
    // Where function is defined as:
    // fun(message) {
    //     print message;
    // }
    ```
    """

    callee: Expr
    args: list[Expr]

    @property
    def literal(self) -> str:
        return f"{self.callee}({', '.join([arg.literal for arg in self.args])})"


@attrs.define(frozen=True)
class GetExpr(Expr):
    """Get a property from an object.

    Examples:
    ```lox
    a.b;
    ```
    """

    obj: Expr
    name: Token

    @property
    def literal(self) -> str:
        return f"{self.obj}.{self.name.lexeme}"


@attrs.define(frozen=True)
class GroupingExpr(Expr):
    """Grouping expression using parantheses.

    Examples:
    ```lox
    (1 + 2) * 3;
    ```
    """

    expr: Expr

    @property
    def literal(self) -> str:
        return f"({self.expr})"


@attrs.define(frozen=True)
class LiteralExpr(Expr):
    """Represents a literal value.

    Args:
        value: The value of the literal.

    Examples:
    ```lox
    1;
    1.0;
    "Hello, world!";
    true;
    false;
    nil;
    ```
    """

    value: object

    @property
    def literal(self) -> str:
        return str(self.value)


@attrs.define(frozen=True)
class LogicalExpr(Expr):
    """Represents a logical expression.

    Examples:
    ```lox
    true or false;
    ```
    """

    left: Expr
    operator: Token
    right: Expr

    @property
    def literal(self) -> str:
        return f"{self.left} {self.operator.lexeme} {self.right}"


@attrs.define(frozen=True)
class SetExpr(Expr):
    """Set a property on an object.

    Examples:
    ```lox
    a.b = 1;
    ```
    """

    obj: Expr
    name: Token
    value: Expr

    @property
    def literal(self) -> str:
        return f"{self.obj}.{self.name.lexeme} = {self.value}"


@attrs.define(frozen=True)
class SuperExpr(Expr):
    """Get a property from a superclass.

    Examples:
    ```lox
    class B {
        bar() {}
    }
    class A < B {
        foo() {
            // Represented by this node.
            super().bar();
        }
    }
    ```
    """

    keyword: Token
    method: Token

    @property
    def literal(self) -> str:
        return f"{self.keyword.lexeme}.{self.method.lexeme}"


@attrs.define(frozen=True)
class ThisExpr(Expr):
    """Get a property from the current object within class.

    Examples:
    ```lox
    class A {
        foo() {}
        bar() {
            this.foo();
        }
    }
    ```
    """

    keyword: Token

    @property
    def literal(self) -> str:
        return self.keyword.lexeme


@attrs.define(frozen=True)
class UnaryExpr(Expr):
    """Represents a unary expression.

    Examples:
    ```lox
    -1;
    !true;
    ```
    """

    operator: Token
    right: Expr

    @property
    def literal(self) -> str:
        return f"{self.operator.lexeme}{self.right}"


@attrs.define(frozen=True)
class VarExpr(Expr):
    """Represents a variable.

    Examples:
    ```lox
    a;
    b;
    ```
    """

    name: Token

    @property
    def literal(self) -> str:
        return self.name.lexeme


R = t.TypeVar("R")


class ExprVisitor(abc.ABC, t.Generic[R]):
    @abc.abstractmethod
    def visit_assign_expr(self, expr: AssignExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_binary_expr(self, expr: BinaryExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_call_expr(self, expr: CallExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_get_expr(self, expr: GetExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_grouping_expr(self, expr: GroupingExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_literal_expr(self, expr: LiteralExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_logical_expr(self, expr: LogicalExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_set_expr(self, expr: SetExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_super_expr(self, expr: SuperExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_this_expr(self, expr: ThisExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_unary_expr(self, expr: UnaryExpr) -> R:
        ...

    @abc.abstractmethod
    def visit_var_expr(self, expr: VarExpr) -> R:
        ...


def visit_expression(expr: Expr, visitor: ExprVisitor[R]) -> R:
    """Visit an expression.

    This is a helper function that is used in place of the traditional visitor pattern.

    In a traditional visitor pattern, each expression would have a `accept` method that
    calls the appropriate method on the visitor. This is a bit verbose and involves a
    lot of indirection. This function is a bit more concise and avoids the indirection.

    I could have used a getattr call, but that would have been a bit more magical and
    less explicit. I prefer this approach.

    Replacing this with a getattr call would look something like this:
    ```python
    return getattr(visitor, f"visit_{type(expr).__name__.lower()}")(expr)
    ```

    Replacing this with a match statement would look something like this:
    ```python
    match expr.__class__.__qualname__:
        case AssignExpr.__qualname__:
            return visitor.visit_assign_expr(expr)
        ...
    ```

    Replacing this with an if statement would look something like this:
    ```python
    if isinstance(expr, AssignExpr):
        return visitor.visit_assign_expr(expr)
    ...
    ```
    This is likely to be the most performant option, but it is also the most verbose.
    One issue with the condition approach is that expressions towards the end of the if
    statements will take longer to evaluate. This is because the interpreter will
    have to evaluate all of the previous expressions before it can get to the one
    that we want. This is not a problem with the dictionary approach.
    """
    mapping = {
        AssignExpr.__qualname__: visitor.visit_assign_expr,
        BinaryExpr.__qualname__: visitor.visit_binary_expr,
        CallExpr.__qualname__: visitor.visit_call_expr,
        GetExpr.__qualname__: visitor.visit_get_expr,
        GroupingExpr.__qualname__: visitor.visit_grouping_expr,
        LiteralExpr.__qualname__: visitor.visit_literal_expr,
        LogicalExpr.__qualname__: visitor.visit_logical_expr,
        SetExpr.__qualname__: visitor.visit_set_expr,
        SuperExpr.__qualname__: visitor.visit_super_expr,
        ThisExpr.__qualname__: visitor.visit_this_expr,
        UnaryExpr.__qualname__: visitor.visit_unary_expr,
        VarExpr.__qualname__: visitor.visit_var_expr,
    }
    return mapping[expr.__class__.__qualname__](t.cast(t.Any, expr))
