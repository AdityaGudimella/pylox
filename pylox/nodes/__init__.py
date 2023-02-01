import typing as t

from pylox.nodes.base import Node as Node

# trunk-ignore(flake8/F401)
from pylox.nodes.expr import AssignExpr as AssignExpr
from pylox.nodes.expr import BinaryExpr as BinaryExpr
from pylox.nodes.expr import CallExpr as CallExpr
from pylox.nodes.expr import Expr as Expr
from pylox.nodes.expr import ExprVisitor as ExprVisitor
from pylox.nodes.expr import GetExpr as GetExpr
from pylox.nodes.expr import GroupingExpr as GroupingExpr
from pylox.nodes.expr import LiteralExpr as LiteralExpr
from pylox.nodes.expr import LogicalExpr as LogicalExpr
from pylox.nodes.expr import SetExpr as SetExpr
from pylox.nodes.expr import SuperExpr as SuperExpr
from pylox.nodes.expr import ThisExpr as ThisExpr
from pylox.nodes.expr import UnaryExpr as UnaryExpr
from pylox.nodes.expr import VarExpr as VarExpr
from pylox.nodes.expr import visit_expression as visit_expression

# trunk-ignore(flake8/F401)
from pylox.nodes.stmt import BlockStmt as BlockStmt
from pylox.nodes.stmt import ClassStmt as ClassStmt
from pylox.nodes.stmt import ExprStmt as ExprStmt
from pylox.nodes.stmt import ForStmt as ForStmt
from pylox.nodes.stmt import FunStmt as FunStmt
from pylox.nodes.stmt import IfStmt as IfStmt
from pylox.nodes.stmt import PrintStmt as PrintStmt
from pylox.nodes.stmt import ReturnStmt as ReturnStmt
from pylox.nodes.stmt import Stmt as Stmt
from pylox.nodes.stmt import StmtVisitor as StmtVisitor
from pylox.nodes.stmt import VarStmt as VarStmt
from pylox.nodes.stmt import WhileStmt as WhileStmt
from pylox.nodes.stmt import visit_statement as visit_statement

R = t.TypeVar("R")


def visit_node(node: Node, visitor: ExprVisitor[R] | StmtVisitor[R]) -> R:
    """Visits a node using the given visitor.

    This is a helper function that is used in place of the traditional visitor pattern.

    In a traditional visitor pattern, each expression would have a `accept` method that
    calls the appropriate method on the visitor. This is a bit verbose and involves a
    lot of indirection. This function is a bit more concise and avoids the indirection.
    """
    if isinstance(node, Expr):
        assert isinstance(visitor, ExprVisitor)
        return visit_expression(node, visitor)
    if isinstance(node, Stmt):
        assert isinstance(visitor, StmtVisitor)
        return visit_statement(node, visitor)
    raise TypeError(f"Unexpected node type: {type(node)}")
