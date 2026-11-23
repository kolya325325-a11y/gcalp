import math


class Calculator:
    def __init__(self) -> None:
        self.display = "0"
        self.stored_value: float | None = None
        self.pending_operator: str | None = None
        self.replace_display = True
        self.last_operator: str | None = None
        self.last_operand: float | None = None
        self.transformed_operand = False
        self.error = False

    def enter_digit(self, digit: str) -> None:
        if self.error:
            self.clear()
        if self.replace_display:
            if self.pending_operator is None:
                self.last_operator = None
                self.last_operand = None
            self.transformed_operand = False
            self.display = digit
            self.replace_display = False
            return
        if len(self.display) < 16:
            self.display = digit if self.display == "0" else self.display + digit

    def enter_decimal(self) -> None:
        if self.error:
            self.clear()
        if self.replace_display:
            if self.pending_operator is None:
                self.last_operator = None
                self.last_operand = None
            self.transformed_operand = False
            self.display = "0."
            self.replace_display = False
        elif "." not in self.display:
            self.display += "."

    def set_operator(self, operator: str) -> None:
        if self.error:
            self.clear()
        current = self._value()
        if self.pending_operator is not None and not self.replace_display:
            current = self._calculate(self.stored_value, current, self.pending_operator)
            if self.error:
                return
            self.display = self._format(current)
        self.stored_value = current
        self.pending_operator = operator
        self.replace_display = True
        self.transformed_operand = False
        self.last_operator = None
        self.last_operand = None

    def equals(self) -> None:
        if self.error:
            return
        if self.pending_operator is not None:
            operand = self._value()
            if self.replace_display and not self.transformed_operand:
                operand = self.stored_value if self.stored_value is not None else operand
            operator = self.pending_operator
            result = self._calculate(self.stored_value, operand, operator)
            if self.error:
                return
            self.display = self._format(result)
            self.last_operator = operator
            self.last_operand = operand
            self.pending_operator = None
            self.stored_value = result
            self.replace_display = True
            self.transformed_operand = False
        elif self.last_operator is not None and self.last_operand is not None:
            result = self._calculate(self._value(), self.last_operand, self.last_operator)
            if self.error:
                return
            self.display = self._format(result)
            self.stored_value = result
            self.replace_display = True

    def percent(self) -> None:
        if self.error:
            return
        current = self._value()
        if self.pending_operator in ("+", "-") and self.stored_value is not None:
            current = self.stored_value * current / 100
        else:
            current /= 100
        self.display = self._format(current)
        self.replace_display = True
        self.transformed_operand = self.pending_operator is not None

    def toggle_sign(self) -> None:
        if self.error:
            return
        value = -self._value()
        self.display = self._format(value)
        self.replace_display = False
        self.transformed_operand = self.pending_operator is not None

    def unary(self, operation: str) -> None:
        if self.error:
            self.clear()
        value = self._value()
        if operation == "square":
            result = value * value
        elif operation == "sqrt":
            if value < 0:
                self._set_error()
                return
            result = math.sqrt(value)
        elif operation == "reciprocal":
            if value == 0:
                self._set_error()
                return
            result = 1 / value
        else:
            raise ValueError(f"Unknown unary operation: {operation}")
        self.display = self._format(result)
        self.replace_display = True
        self.transformed_operand = self.pending_operator is not None

    def backspace(self) -> None:
        if self.error:
            self.clear()
        elif not self.replace_display:
            self.display = self.display[:-1] or "0"
            if self.display == "-":
                self.display = "0"

    def clear_entry(self) -> None:
        self.display = "0"
        self.replace_display = True
        self.transformed_operand = False
        self.error = False

    def clear(self) -> None:
        self.display = "0"
        self.stored_value = None
        self.pending_operator = None
        self.replace_display = True
        self.transformed_operand = False
        self.last_operator = None
        self.last_operand = None
        self.error = False

    def _value(self) -> float:
        return float(self.display)

    def _calculate(self, left: float | None, right: float, operator: str) -> float:
        if left is None:
            return right
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                self._set_error()
                return 0
            return left / right
        raise ValueError(f"Unknown operator: {operator}")

    def _set_error(self) -> None:
        self.display = "Невозможно"
        self.pending_operator = None
        self.stored_value = None
        self.last_operator = None
        self.last_operand = None
        self.replace_display = True
        self.transformed_operand = False
        self.error = True

    @staticmethod
    def _format(value: float) -> str:
        if not math.isfinite(value):
            return "Ошибка"
        return f"{value:.12g}"
