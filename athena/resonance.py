import ast
from typing import Any, Dict, List, Tuple


def _safe_eval(expr: str, scope: Dict[str, Any]) -> Any:
    tree = ast.parse(expr, mode="eval")
    allowed_calls = {"min", "max", "abs"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Attribute, ast.Subscript, ast.Import, ast.ImportFrom, ast.Lambda)):
            raise ValueError("Unsafe expression in DSL")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in allowed_calls:
                raise ValueError("Unsafe expression in DSL")
    return eval(compile(tree, "<dsl>", "eval"), {"__builtins__": {}, "min": min, "max": max, "abs": abs}, scope)


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
            scope[name] = scope.get(name, 0.0) + float(_safe_eval(expr.strip(), scope))
            return
        if "-=" in stmt:
            name, expr = stmt.split("-=", 1)
            name = name.strip()
            scope[name] = scope.get(name, 0.0) - float(_safe_eval(expr.strip(), scope))
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
