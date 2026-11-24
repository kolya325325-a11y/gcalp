"""Инженерный калькулятор и его математические функции."""

import math

from .standard import StandardCalculator
from .common import FUNCTIONS, OPERATORS


class EngineeringCalculator(StandardCalculator):
    """Калькулятор с инженерными функциями и тригонометрией."""

    def enter_function(self, function_name: str) -> None:
        """Добавляет вызов функции с аргументом, который будет вычислен целиком."""
        if function_name not in FUNCTIONS:
            raise ValueError(f"Unknown function: {function_name}")
        if self.error or self.finished:
            self.clear()
        if self.tokens and self.tokens[-1] not in OPERATORS and self.tokens[-1] != "(":
            self.tokens.append("*")
        self.tokens.extend((function_name, "("))
        self.replace_display = True
        self._refresh_expression()

    def unary(self, operation: str) -> None:
        """Вычисляет унарную инженерную операцию."""
        if self.error:
            self.clear()
        try:
            value = self._operand_value()
            if operation not in FUNCTIONS:
                raise ValueError(f"Unknown unary operation: {operation}")
            self._set_operand(self._apply_function(operation, value))
        except (ArithmeticError, ValueError, SyntaxError, RecursionError):
            self._set_error()

    def toggle_angle_mode(self) -> None:
        """Переключает единицы измерения тригонометрических функций."""
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"

    def constant(self, name: str) -> None:
        """Подставляет математическую константу в текущий операнд."""
        constants = {"pi": math.pi, "e": math.e}
        if name not in constants:
            raise ValueError(f"Unknown constant: {name}")
        if self.error or self.finished:
            self.clear()
        self._set_operand(constants[name])

    def _apply_function(self, function_name: str, value: float) -> float:
        """Вычисляет функцию с учётом выбранной угловой единицы."""
        if function_name in ("sin", "cos", "tan"):
            argument = math.radians(value) if self.angle_mode == "DEG" else value
            return FUNCTIONS[function_name](argument)
        if function_name in ("asin", "acos", "atan"):
            result = FUNCTIONS[function_name](value)
            return math.degrees(result) if self.angle_mode == "DEG" else result
        return FUNCTIONS[function_name](value)

__all__ = ["EngineeringCalculator"]
