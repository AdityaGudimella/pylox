import abc
import contextlib
import typing as t

import attrs
import rich

from pylox import nodes as pn
from pylox.environment import Environment
from pylox.errors import PyloxReturn, PyloxRuntimeError
from pylox.token import TokenType

P = t.ParamSpec("P")
R = t.TypeVar("R")


class LoxCallable(abc.ABC, t.Generic[P, R]):
    @property
    @abc.abstractmethod
    def arity(self) -> int:
        ...

    @abc.abstractmethod
    def __call__(
        self, interpreter: "Interpreter", *args: P.args, **kwargs: P.kwargs
    ) -> R:
        ...


@attrs.define()
class LoxFunction(LoxCallable[[t.Any], t.Any]):
    closure: Environment
    declaration: pn.FunStmt

    @property
    def arity(self) -> int:
        return len(self.declaration.params)

    def __call__(self, interpreter: "Interpreter", *args: t.Any) -> t.Any:
        env = Environment(self.closure)
        if len(args) != self.arity:
            raise PyloxRuntimeError.from_token(
                f"Expected {self.arity} arguments but got {len(args)}.",
                self.declaration.name,
            )
        for param, arg in zip(self.declaration.params, args):
            env.define(param.lexeme, arg)
        try:
            with interpreter.env_scope(env):
                interpreter.execute(self.declaration.body)
        except PyloxReturn as ret:
            return ret.value


@attrs.define()
class Distances(t.MutableMapping[pn.Expr, int]):
    data: dict[int, int] = attrs.field(init=False, factory=dict)
    exprs: dict[int, pn.Expr] = attrs.field(init=False, factory=dict)

    def __getitem__(self, item: pn.Expr) -> int:
        self.exprs[id(item)] = item
        return self.data[id(item)]

    def __setitem__(self, item: pn.Expr, value: int) -> None:
        self.data[id(item)] = value

    def __delitem__(self, item: pn.Expr) -> None:
        self.data.pop(id(item))
        self.exprs.pop(id(item))

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> t.Iterator[pn.Expr]:
        return iter(self.exprs.values())

    def __repr__(self) -> str:
        return repr({self.exprs[k].literal: v for k, v in self.data.items()})


@attrs.define()
class Interpreter(pn.ExprVisitor[t.Any], pn.StmtVisitor[None]):
    """Interprets a list of statements.

    Args:
        global_env (Enviroment): The global environment to use.
        test_console (list[str]): A list to append console output to. This is only
            used for testing.

    IMPORTANT:
        This interpreter does not define any builtin functions / variables. There exists
        a separate class for that: `EnvironmentWithBuiltins`. It is up to the user to
        create an interpreter with the correct environment. This is done to avoid
        circular imports.
    """

    global_env: Environment = attrs.field(factory=Environment)
    test_console: list[str] = attrs.field(factory=list)

    _env: Environment = attrs.field(init=False)
    _locals: Distances = attrs.field(init=False, factory=Distances)

    def __attrs_post_init__(self) -> None:
        self._env = self.global_env

    @property
    def env(self) -> Environment:
        return self._env

    def interpret(self, *nodes: pn.Node) -> None:
        for node in nodes:
            pn.visit_node(node, self)

    def execute(self, stmt: pn.Stmt) -> None:
        pn.visit_node(stmt, self)

    def evaluate(self, expr: pn.Expr) -> t.Any:
        return pn.visit_node(expr, self)

    def visit_assign_expr(self, expr: pn.AssignExpr) -> t.Any:
        value = self.evaluate(expr.value)

        distance = self._locals.get(expr)
        if distance is not None:
            self._env.assign_at(distance, expr.name.lexeme, value)
        else:
            self.global_env.assign(expr.name.lexeme, value)
        return value

    def visit_binary_expr(self, expr: pn.BinaryExpr) -> t.Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.PLUS:
                self.ensure_types((float, str), left, right)
                return left + right
            case TokenType.MINUS:
                self.ensure_types(float, left, right)
                return left - right
            case TokenType.STAR:
                self.ensure_types(float, left, right)
                return left * right
            case TokenType.SLASH:
                self.ensure_types(float, left, right)
                return left / right
            case TokenType.GREATER:
                self.ensure_types(float, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.ensure_types(float, left, right)
                return left >= right
            case TokenType.LESS:
                self.ensure_types(float, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.ensure_types(float, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case _:
                raise NotImplementedError(f"for operator: {expr.operator.lexeme}")

    def visit_call_expr(self, expr: pn.CallExpr) -> t.Any:
        func = self.evaluate(expr.callee)
        if not isinstance(func, LoxCallable):
            raise RuntimeError(f"{expr.callee.literal} is not callable.")
        if func.arity != len(expr.args):
            raise RuntimeError(
                f"Expected {func.arity} arguments but got {len(expr.args)}."
            )
        args = [self.evaluate(arg) for arg in expr.args]
        return func(self, *args)  # type: ignore

    def visit_get_expr(self, expr: pn.GetExpr) -> t.Any:
        raise NotImplementedError

    def visit_grouping_expr(self, expr: pn.GroupingExpr) -> t.Any:
        return self.evaluate(expr.expr)

    def visit_literal_expr(self, expr: pn.LiteralExpr) -> t.Any:
        return expr.value

    def visit_logical_expr(self, expr: pn.LogicalExpr) -> t.Any:
        left = self.evaluate(expr.left)
        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        elif not self.is_truthy(left):
            return left
        right = self.evaluate(expr.right)
        return right

    def visit_set_expr(self, expr: pn.SetExpr) -> t.Any:
        raise NotImplementedError

    def visit_super_expr(self, expr: pn.SuperExpr) -> t.Any:
        raise NotImplementedError

    def visit_this_expr(self, expr: pn.ThisExpr) -> t.Any:
        raise NotImplementedError

    def visit_unary_expr(self, expr: pn.UnaryExpr) -> t.Any:
        right = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS:
                self.ensure_types(float, right)
                return -right
            case TokenType.BANG:
                return not self.is_truthy(right)
            case _:
                raise NotImplementedError(f"for operator: {expr.operator.lexeme}")

    def visit_var_expr(self, expr: pn.VarExpr) -> t.Any:
        return self.lookup_variable(expr)

    def visit_block_stmt(self, stmt: pn.BlockStmt) -> None:
        with self.env_scope(Environment(enclosing=self._env)):
            for s in stmt.statements:
                self.execute(s)

    def visit_class_stmt(self, stmt: pn.ClassStmt) -> None:
        raise NotImplementedError

    def visit_expr_stmt(self, stmt: pn.ExprStmt) -> None:
        self.evaluate(stmt.expr)

    def visit_fun_stmt(self, stmt: pn.FunStmt) -> None:
        self._env.define(
            stmt.name.lexeme, LoxFunction(closure=self.env, declaration=stmt)
        )

    def visit_for_stmt(self, stmt: pn.ForStmt) -> None:
        with self.env_scope(Environment(enclosing=self._env)):
            if stmt.initializer is not None:
                print(stmt.initializer)
                self.execute(stmt.initializer)
            while True:
                if stmt.condition is not None:
                    condition = self.evaluate(stmt.condition)
                    if not self.is_truthy(condition):
                        break
                self.execute(stmt.body)
                if stmt.increment is not None:
                    self.evaluate(stmt.increment)

    def visit_if_stmt(self, stmt: pn.IfStmt) -> None:
        condition = self.evaluate(stmt.condition)
        if self.is_truthy(condition):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: pn.PrintStmt) -> None:
        value = self.evaluate(stmt.expr)
        as_str = self.as_str(value)
        self.test_console.append(as_str)
        rich.print(as_str)

    def visit_return_stmt(self, stmt: pn.ReturnStmt) -> None:
        raise PyloxReturn(self.evaluate(stmt.value) if stmt.value else None)

    def visit_var_stmt(self, stmt: pn.VarStmt) -> None:
        self._env.define(
            stmt.name.lexeme,
            self.evaluate(stmt.initializer) if stmt.initializer else None,
        )

    def visit_while_stmt(self, stmt: pn.WhileStmt) -> None:
        while True:
            condition = self.evaluate(stmt.condition)
            if not self.is_truthy(condition):
                break
            self.execute(stmt.body)

    def ensure_types(self, types: type | tuple[type, ...], *values: t.Any) -> None:
        for value in values:
            if not isinstance(value, types):
                raise TypeError(f"Invalid type: {value}. Expected types: {types}")

    def is_truthy(self, value: t.Any) -> bool:
        """Returns whether the value is truthy or not.

        NOTE: In Lox, only `nil` and `False` are falsy. This follows Ruby's behavior.
        """
        if value is None:
            return False
        return value if isinstance(value, bool) else True

    def as_str(self, value: t.Any) -> str:
        """Returns the string representation of the value."""
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    @contextlib.contextmanager
    def env_scope(self, env: Environment) -> t.Iterator[None]:
        """Replaces self._env with env when in scope."""
        old_env = self._env
        self._env = env
        try:
            yield
        finally:
            self._env = old_env

    def resolve(self, expr: pn.Expr, depth: int) -> None:
        self._locals[expr] = depth

    def lookup_variable(self, expr: pn.VarExpr) -> t.Any:
        """Returns the value of a variable."""
        depth = self._locals.get(expr)
        if depth is not None:
            return self._env.get_at(depth, expr.name.lexeme)
        return self.global_env.get(expr.name.lexeme)
