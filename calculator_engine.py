import math


class Calculator:
    """Хранит состояние калькулятора и выполняет операции без зависимости от Tkinter."""

    def __init__(self) -> None:
        """Создаёт начальное состояние калькулятора."""
        # Строка дисплея хранится отдельно от чисел, чтобы сохранить ввод вроде "0.".
        self.display = "0"
        self.expression = ""
        self.stored_value: float | None = None
        self.pending_operator: str | None = None
        # True, когда следующий ввод цифры должен заменить экранное значение.
        self.replace_display = True
        self.last_operator: str | None = None
        self.last_operand: float | None = None
        # Не подменять операнд сохранённым значением после %, √x, x² или смены знака.
        self.transformed_operand = False
        self.error = False

    def enter_digit(self, digit: str) -> None:
        """Добавляет цифру к текущему числу или начинает его ввод."""
        if self.error:
            self.clear()
        if self.replace_display:
            # После результата начинаем новое вычисление, если оператор не ожидается.
            if self.pending_operator is None:
                self.expression = ""
                self.last_operator = None
                self.last_operand = None
            self.transformed_operand = False
            self.display = digit
            self.replace_display = False
            self._update_expression_operand()
            return
        if len(self.display) < 16:
            self.display = digit if self.display == "0" else self.display + digit
            self._update_expression_operand()

    def enter_decimal(self) -> None:
        """Добавляет десятичный разделитель к текущему числу."""
        if self.error:
            self.clear()
        # При начале нового ввода сразу показываем ноль перед разделителем.
        if self.replace_display:
            if self.pending_operator is None:
                self.expression = ""
                self.last_operator = None
                self.last_operand = None
            self.transformed_operand = False
            self.display = "0."
            self.replace_display = False
            self._update_expression_operand()
        elif "." not in self.display:
            self.display += "."
            self._update_expression_operand()

    def set_operator(self, operator: str) -> None:
        """Запоминает оператор или сначала вычисляет предыдущую операцию."""
        if self.error:
            self.clear()
        current = self._value()
        if self.pending_operator is None:
            self.expression = self._format(current)
        elif self.replace_display and not self.transformed_operand:
            previous_symbol = self._operator_symbol(self.pending_operator)
            # Повторный оператор заменяет ожидающий, если новое число ещё не введено.
            self.expression = self.expression.removesuffix(f" {previous_symbol}")
        self.expression += f" {self._operator_symbol(operator)}"
        if self.pending_operator is not None and not self.replace_display:
            # Последовательные операции выполняются слева направо, как в стандартном калькуляторе.
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
        """Выполняет ожидающую операцию либо повторяет предыдущую."""
        if self.error:
            return
        if self.pending_operator is not None:
            operand = self._value()
            if self.replace_display and not self.transformed_operand:
                # Для ввода вроде "5 +" повторяем первое число как правый операнд.
                operand = self.stored_value if self.stored_value is not None else operand
                self._update_expression_operand(self._format(operand))
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
            # Повторное нажатие "=" повторяет последнюю операцию с тем же операндом.
            result = self._calculate(self._value(), self.last_operand, self.last_operator)
            if self.error:
                return
            self.display = self._format(result)
            self.stored_value = result
            self.replace_display = True

    def percent(self) -> None:
        """Преобразует текущее число в процент или процент от первого операнда."""
        if self.error:
            return
        current = self._value()
        if self.pending_operator in ("+", "-") and self.stored_value is not None:
            # При сложении и вычитании процент считается от первого числа выражения.
            current = self.stored_value * current / 100
        else:
            current /= 100
        self.display = self._format(current)
        self.replace_display = True
        self.transformed_operand = self.pending_operator is not None
        self._update_expression_operand()

    def toggle_sign(self) -> None:
        """Меняет знак текущего числа на противоположный."""
        if self.error:
            return
        # После изменения знака число остаётся редактируемым.
        value = -self._value()
        self.display = self._format(value)
        self.replace_display = False
        self.transformed_operand = self.pending_operator is not None
        self._update_expression_operand()

    def unary(self, operation: str) -> None:
        """Выполняет квадрат, квадратный корень или обратное число."""
        if self.error:
            self.clear()
        value = self._value()
        if operation == "square":
            result = value * value
        elif operation == "sqrt":
            if value < 0:
                # Для отрицательного числа корень в вещественных числах не определён.
                self._set_error()
                return
            result = math.sqrt(value)
        elif operation == "reciprocal":
            if value == 0:
                # Обратное число для нуля не существует.
                self._set_error()
                return
            result = 1 / value
        else:
            raise ValueError(f"Unknown unary operation: {operation}")
        self.display = self._format(result)
        self.replace_display = True
        self.transformed_operand = self.pending_operator is not None
        self._update_expression_operand()

    def backspace(self) -> None:
        """Удаляет последний введённый символ текущего числа."""
        if self.error:
            self.clear()
        elif not self.replace_display:
            # Удаляем символ только из текущего вводимого числа.
            self.display = self.display[:-1] or "0"
            if self.display == "-":
                self.display = "0"
            self._update_expression_operand()

    def clear_entry(self) -> None:
        """Очищает текущее число, сохраняя остальные части вычисления."""
        # CE сбрасывает текущее число, но сохраняет накопленное выражение.
        self.display = "0"
        self.replace_display = True
        self.transformed_operand = False
        self.error = False
        self._update_expression_operand()

    def clear(self) -> None:
        """Полностью сбрасывает число и состояние вычисления."""
        # C сбрасывает и число, и ожидающую операцию, и строку выражения.
        self.display = "0"
        self.expression = ""
        self.stored_value = None
        self.pending_operator = None
        self.replace_display = True
        self.transformed_operand = False
        self.last_operator = None
        self.last_operand = None
        self.error = False

    def _value(self) -> float:
        """Возвращает отображаемое значение как число."""
        # К этой точке display содержит числовой текст, а не сообщение об ошибке.
        return float(self.display)

    def _update_expression_operand(self, value: str | None = None) -> None:
        """Обновляет последний операнд в строке отображаемого выражения."""
        if self.pending_operator is None:
            return
        operand = self.display if value is None else value
        suffix = f" {self._operator_symbol(self.pending_operator)}"
        if self.expression.endswith(suffix):
            self.expression += f" {operand}"
        else:
            # Обновляем последний операнд в строке, не затрагивая предыдущие вычисления.
            prefix = self.expression.rsplit(" ", 1)[0]
            self.expression = f"{prefix} {operand}"

    @staticmethod
    def _operator_symbol(operator: str) -> str:
        """Возвращает символ оператора в формате интерфейса."""
        # Символы умножения и деления отличаются от клавиатурных операторов.
        return {"+": "+", "-": "−", "*": "×", "/": "÷"}[operator]

    def _calculate(self, left: float | None, right: float, operator: str) -> float:
        """Вычисляет результат одной арифметической операции."""
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
                # Переводим деление на ноль в видимое состояние ошибки интерфейса.
                self._set_error()
                return 0
            return left / right
        raise ValueError(f"Unknown operator: {operator}")

    def _set_error(self) -> None:
        """Переводит вычислитель в состояние ошибки и сбрасывает операцию."""
        # Сообщение ошибки заменяет число на дисплее до следующего ввода.
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
        """Форматирует число для компактного отображения."""
        if not math.isfinite(value):
            return "Ошибка"
        # Форматируем результат с точностью до 12 значащих цифр.
        return f"{value:.12g}"
