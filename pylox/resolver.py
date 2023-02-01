import contextlib
import typing as t

import attrs

from pylox import nodes as pn
from pylox.constants import ClassType, FunctionType
from pylox.errors import Errors, PyloxResolverError
from pylox.interpreter import Interpreter
from pylox.token import Token

T = t.TypeVar("T")


@attrs.define()
class Scopes:
    errors: Errors = attrs.field(factory=Errors)
    scopes: list[dict[str, bool]] = attrs.field(init=False, factory=list)

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, token: Token) -> None:
        if not self.scopes:
            return
        if (name := token.lexeme) in self.scopes[-1]:
            raise self.errors.record(
                PyloxResolverError.from_token(
                    message=f"Variable with name: {name} already exists in scope",
                    token=token,
                )
            )
        self.scopes[-1][name] = False

    def define(self, token: Token) -> None:
        if not self.scopes:
            return
        self.scopes[-1][token.lexeme] = True

    def is_defined_in_current_scope(self, token: Token) -> bool:
        return token.lexeme in self.scopes[-1] if self.scopes else False

    def is_initialized_in_current_scope(self, token: Token) -> bool:
        if not self.scopes:
            return False
        if token.lexeme not in self.scopes[-1]:
            return False
        return self.scopes[-1][token.lexeme]

    def get_distance(self, token: Token) -> int:
        for i, scope in enumerate(reversed(self.scopes)):
            if token.lexeme in scope:
                return i
        raise ValueError(f"Variable with name: {token.lexeme} not found")

    def __bool__(self) -> bool:
        return bool(self.scopes)


@attrs.define()
class Resolver(pn.ExprVisitor[None], pn.StmtVisitor[None]):
    interpreter: Interpreter
    errors: Errors = attrs.field(factory=Errors)

    _scopes: Scopes = attrs.field(init=False)
    _current_function: FunctionType = attrs.field(init=False, default=FunctionType.NONE)
    _current_class: ClassType = attrs.field(init=False, default=ClassType.NONE)

    def __attrs_post_init__(self) -> None:
        self._scopes = Scopes(errors=self.errors)

    def resolve(self, *nodes: pn.Node) -> None:
        for node in nodes:
            pn.visit_node(node, self)

    def visit_block_stmt(self, stmt: pn.BlockStmt) -> None:
        self._scopes.begin_scope()
        self.resolve(*stmt.statements)
        self._scopes.end_scope()

    def visit_class_stmt(self, stmt: pn.ClassStmt) -> None:
        ...

    def visit_expr_stmt(self, stmt: pn.ExprStmt) -> None:
        self.resolve(stmt.expr)

    def visit_for_stmt(self, stmt: pn.ForStmt) -> None:
        for node in (stmt.initializer, stmt.condition, stmt.increment, stmt.body):
            if node is not None:
                self.resolve(node)

    def visit_fun_stmt(self, stmt: pn.FunStmt) -> None:
        self._scopes.declare(stmt.name)
        self._scopes.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: pn.IfStmt) -> None:
        self.resolve(stmt.condition, stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: pn.PrintStmt) -> None:
        self.resolve(stmt.expr)

    def visit_return_stmt(self, stmt: pn.ReturnStmt) -> None:
        if self._current_function == FunctionType.NONE:
            raise self.errors.record(
                PyloxResolverError.from_token(
                    message="Cannot return from top-level code",
                    token=stmt.keyword,
                )
            )

        if stmt.value is not None:
            if self._current_function == FunctionType.INITIALIZER:
                raise self.errors.record(
                    PyloxResolverError.from_token(
                        message="Cannot return a value from an initializer",
                        token=stmt.keyword,
                    )
                )
            self.resolve(stmt.value)

    def visit_var_stmt(self, stmt: pn.VarStmt) -> None:
        self._scopes.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self._scopes.define(stmt.name)

    def visit_while_stmt(self, stmt: pn.WhileStmt) -> None:
        self.resolve(stmt.condition, stmt.body)

    def visit_assign_expr(self, expr: pn.AssignExpr) -> None:
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: pn.BinaryExpr) -> None:
        self.resolve(expr.left, expr.right)

    def visit_call_expr(self, expr: pn.CallExpr) -> None:
        self.resolve(expr.callee, *expr.args)

    def visit_get_expr(self, expr: pn.GetExpr) -> None:
        self.resolve(expr.obj)

    def visit_grouping_expr(self, expr: pn.GroupingExpr) -> None:
        self.resolve(expr.expr)

    def visit_literal_expr(self, expr: pn.LiteralExpr) -> None:
        pass

    def visit_logical_expr(self, expr: pn.LogicalExpr) -> None:
        self.resolve(expr.left, expr.right)

    def visit_set_expr(self, expr: pn.SetExpr) -> None:
        self.resolve(expr.value, expr.obj)

    def visit_super_expr(self, expr: pn.SuperExpr) -> None:
        if self._current_class == ClassType.NONE:
            raise self.errors.record(
                PyloxResolverError.from_token(
                    message="Cannot use 'super' outside of a class",
                    token=expr.keyword,
                )
            )
        elif self._current_class != ClassType.SUBCLASS:
            raise self.errors.record(
                PyloxResolverError.from_token(
                    message="Cannot use 'super' in a class with no superclass",
                    token=expr.keyword,
                )
            )
        self.resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr: pn.ThisExpr) -> None:
        if self._current_class == ClassType.NONE:
            raise self.errors.record(
                PyloxResolverError.from_token(
                    message="Cannot use 'this' outside of a class",
                    token=expr.keyword,
                )
            )
        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr: pn.UnaryExpr) -> None:
        self.resolve(expr.right)

    def visit_var_expr(self, expr: pn.VarExpr) -> None:
        if all(
            (
                self._scopes,
                self._scopes.is_defined_in_current_scope(expr.name),
                not self._scopes.is_initialized_in_current_scope(expr.name),
            )
        ):
            raise self.errors.record(
                PyloxResolverError.from_token(
                    message="Cannot read local variable in its own initializer",
                    token=expr.name,
                )
            )
        self.resolve_local(expr, expr.name)

    def resolve_local(self, expr: pn.Expr, token: Token) -> None:
        with contextlib.suppress(ValueError):
            self.interpreter.resolve(expr, self._scopes.get_distance(token))

    def resolve_function(self, stmt: pn.FunStmt, function_type: FunctionType) -> None:
        enclosing_function = self._current_function
        self._current_function = function_type
        self._scopes.begin_scope()
        for param in stmt.params:
            self._scopes.declare(param)
            self._scopes.define(param)
        self.resolve(stmt.body)
        self._scopes.end_scope()
        self._current_function = enclosing_function
