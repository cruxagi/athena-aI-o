import ast
from typing import Any, Dict, List, Tuple


class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, scope: Dict[str, Any]) -> None:
        self.scope = scope
        self.funcs = {"min": min, "max": max, "abs": abs}

    def eval(self, expr: str) -> Any:
        tree = ast.parse(expr, mode="eval")
        return self.visit(tree.body)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ValueError("Division by zero")
            return left / right
        if isinstance(node.op, ast.Mod):
            if right == 0:
                raise ValueError("Division by zero")
            return left % right
        raise ValueError("Unsupported binary operator")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operator")

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported literal")

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in self.scope:
            return self.scope[node.id]
        raise ValueError(f"Unknown name {node.id}")

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name) or node.func.id not in self.funcs:
            raise ValueError("Unsafe call")
        args = [self.visit(arg) for arg in node.args]
        return self.funcs[node.func.id](*args)

    def visit_Compare(self, node: ast.Compare) -> Any:
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise ValueError("Unsupported comparison")
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])
        op = node.ops[0]
        if isinstance(op, ast.Lt):
            return left < right
        if isinstance(op, ast.Gt):
            return left > right
        if isinstance(op, ast.LtE):
            return left <= right
        if isinstance(op, ast.GtE):
            return left >= right
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        raise ValueError("Unsupported comparison operator")

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        values = [self.visit(v) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
        raise ValueError("Unsupported boolean operator")

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError("Unsupported expression")


def _safe_eval(expr: str, scope: Dict[str, Any]) -> Any:
    value = SafeEvaluator(scope).eval(expr)
    if not isinstance(value, (int, float)):
        raise ValueError("Expression must be numeric")
    return float(value)


class ResonanceController:
    """Minimal runtime DSL for programming macro-layer behavior."""

    def __init__(self) -> None:
        self.functions: Dict[str, List[Any]] = {}

    def _parse_block(self, lines: List[str], start: int = 0) -> Tuple[List[Any], int]:
        block: List[Any] = []
        i = start
        while i < len(lines):
            raw = lines[i].strip()
            if not raw:
                i += 1
                continue
            if raw.startswith("}"):
                return block, i + 1
            if raw.startswith("fn "):
                name = raw[3:].split("{")[0].strip()
                body, i = self._parse_block(lines, i + 1)
                self.functions[name] = body
                continue
            if raw.startswith("if "):
                condition = raw[3:].split("{")[0].strip()
                true_body, i = self._parse_block(lines, i + 1)
                false_body: List[Any] = []
                if i < len(lines) and lines[i].strip().startswith("else"):
                    false_body, i = self._parse_block(lines, i + 1)
                block.append(("if", condition, true_body, false_body))
                continue
            block.append(("stmt", raw))
            i += 1
        return block, i

    def _exec_block(self, block: List[Any], scope: Dict[str, Any]) -> None:
        for entry in block:
            kind = entry[0]
            if kind == "if":
                _, condition, true_body, false_body = entry
                branch = true_body if _safe_eval(condition, scope) else false_body
                self._exec_block(branch, scope)
                continue
            _, stmt = entry
            if stmt.endswith("}"):
                continue
            if stmt.endswith("()") and stmt[:-2] in self.functions:
                self._exec_block(self.functions[stmt[:-2]], scope)
                continue
            if "=" in stmt:
                self._apply_assignment(stmt, scope)

    def _apply_assignment(self, stmt: str, scope: Dict[str, Any]) -> None:
        stmt = stmt.strip()
        if "+=" in stmt:
            name, expr = stmt.split("+=", 1)
            name = name.strip()
            scope[name] = scope.get(name, 0.0) + _safe_eval(expr.strip(), scope)
            return
        if "-=" in stmt:
            name, expr = stmt.split("-=", 1)
            name = name.strip()
            scope[name] = scope.get(name, 0.0) - _safe_eval(expr.strip(), scope)
            return
        if "=" in stmt:
            name, expr = stmt.split("=", 1)
            scope[name.strip()] = _safe_eval(expr.strip(), scope)

    def run(self, program: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        if not program.strip():
            return scope
        lines = [line for line in program.replace("{", "{\n").replace("}", "}\n").splitlines() if line.strip()]
        block, _ = self._parse_block(lines)
        self._exec_block(block, scope)
        return scope
