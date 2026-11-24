"""Графический калькулятор и вычисление функций от x."""

import ast
import math

from .common import FUNCTIONS, OPERATORS
from .engineering import EngineeringCalculator


class GraphingCalculator(EngineeringCalculator):
    """Калькулятор, совместимый с графическим режимом интерфейса."""

    def evaluate_graph(self, expression: str, x_value: float) -> float:
        """Вычисляет графическое выражение для одного значения x."""
        normalized = (
            expression.replace("^", "**")
            .replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace("π", "pi")
        )
        if "log(" in normalized:
            normalized = normalized.replace("log(", "log10(")
        tree = ast.parse(normalized, mode="eval").body
        return self._evaluate_graph_node(tree, x_value)

    def _evaluate_graph_node(self, node: ast.AST, x_value: float) -> float:
        """Вычисляет узел графика с разрешёнными переменными и функциями."""
        if isinstance(node, ast.Name):
            if node.id == "x":
                return x_value
            if node.id == "pi":
                return math.pi
            if node.id == "e":
                return math.e
            raise ValueError("Unknown graph variable")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = self._evaluate_graph_node(node.operand, x_value)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            operator_name = self._operator_from_node(node.op)
            return OPERATORS[operator_name](
                self._evaluate_graph_node(node.left, x_value),
                self._evaluate_graph_node(node.right, x_value),
            )
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in FUNCTIONS
            and len(node.args) == 1
            and not node.keywords
        ):
            return self._apply_function(
                node.func.id, self._evaluate_graph_node(node.args[0], x_value)
            )
        raise ValueError("Unsupported graph expression")

__all__ = ["GraphingCalculator"]
