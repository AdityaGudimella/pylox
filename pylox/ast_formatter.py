from pylox import nodes as pn
from pylox.token import Token


class ASTFormatter(pn.ExprVisitor[str], pn.StmtVisitor[str]):
    def visit_assign_expr(self, expr: pn.AssignExpr) -> str:
        return self.parenthesize("=", expr.name.lexeme, expr.value)

    def visit_binary_expr(self, expr: pn.BinaryExpr) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_call_expr(self, expr: pn.CallExpr) -> str:
        return self.parenthesize("call", expr.callee.literal, *expr.args)

    def visit_get_expr(self, expr: pn.GetExpr) -> str:
        return self.parenthesize("get", expr.obj.literal, expr.name.lexeme)

    def visit_grouping_expr(self, expr: pn.GroupingExpr) -> str:
        return self.parenthesize("group", expr.expr)

    def visit_literal_expr(self, expr: pn.LiteralExpr) -> str:
        return "nil" if expr.value is None else str(expr.value)

    def visit_logical_expr(self, expr: pn.LogicalExpr) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_set_expr(self, expr: pn.SetExpr) -> str:
        return self.parenthesize("set", expr.obj.literal, expr.name.lexeme, expr.value)

    def visit_super_expr(self, expr: pn.SuperExpr) -> str:
        return self.parenthesize("super", expr.keyword.lexeme, expr.method.lexeme)

    def visit_this_expr(self, expr: pn.ThisExpr) -> str:
        return "this"

    def visit_unary_expr(self, expr: pn.UnaryExpr) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_var_expr(self, expr: pn.VarExpr) -> str:
        return expr.name.lexeme

    def visit_block_stmt(self, stmt: pn.BlockStmt) -> str:
        return f"(block {' '.join(pn.visit_node(s, self) for s in stmt.statements)})"

    def visit_class_stmt(self, stmt: pn.ClassStmt) -> str:
        class_ = f"class {stmt.name.lexeme}"
        superclass = (
            f" < {pn.visit_node(stmt.superclass, self)}" if stmt.superclass else ""
        )
        methods = " ".join(pn.visit_node(m, self) for m in stmt.methods)
        return f"({class_}{superclass} {methods})"

    def visit_expr_stmt(self, stmt: pn.ExprStmt) -> str:
        return self.parenthesize(";", stmt.expr)

    def visit_fun_stmt(self, stmt: pn.FunStmt) -> str:
        fun = f"fun {stmt.name.lexeme}"
        params = " ".join(p.lexeme for p in stmt.params)
        body = pn.visit_node(stmt.body, self)
        return f"({fun} ({params}) {body})"

    def visit_for_stmt(self, stmt: pn.ForStmt) -> str:
        return self.parenthesize(
            "for",
            stmt.initializer or ";",
            stmt.condition or "true",
            stmt.increment or ";",
            stmt.body,
        )

    def visit_if_stmt(self, stmt: pn.IfStmt) -> str:
        return self.parenthesize(
            "if", stmt.condition, stmt.then_branch, stmt.else_branch or ""
        )

    def visit_print_stmt(self, stmt: pn.PrintStmt) -> str:
        return self.parenthesize("print", stmt.expr)

    def visit_return_stmt(self, stmt: pn.ReturnStmt) -> str:
        return self.parenthesize("return", stmt.value or "nil")

    def visit_var_stmt(self, stmt: pn.VarStmt) -> str:
        return self.parenthesize(
            "var", stmt.name.lexeme, "=", stmt.initializer or "nil"
        )

    def visit_while_stmt(self, stmt: pn.WhileStmt) -> str:
        return self.parenthesize("while", stmt.condition, stmt.body)

    def parenthesize(
        self, name: str, *parts: pn.Node | Token | list[pn.Node | Token | str] | str
    ) -> str:
        return f"({name}{self.transform(*parts)})"

    def transform(
        self, *parts: pn.Node | Token | list[pn.Node | Token | str] | str
    ) -> str:
        result: list[str] = []
        for part in parts:
            result.append(" ")
            if isinstance(part, pn.Node):
                result.append(pn.visit_node(part, self))
            elif isinstance(part, Token):
                result.append(part.lexeme)
            elif isinstance(part, list):
                result.append(self.transform(*part))
            else:
                result.append(part)
        return "".join(result)
