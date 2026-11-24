import ast
import math
import operator


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "**": operator.pow,
}
SYMBOLS = {"+": "+", "-": "−", "*": "×", "/": "÷", "**": "^"}
FUNCTIONS = {
    "square": lambda value: value * value,
    "cube": lambda value: value**3,
    "sqrt": math.sqrt,
    "reciprocal": lambda value: 1 / value,
    "abs": abs,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "ln": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "ten_power": lambda value: 10**value,
    "factorial": lambda value: math.factorial(int(value))
    if value >= 0 and value.is_integer()
    else (_ for _ in ()).throw(ValueError("Factorial domain")),
}


class BaseCalculator:
    """Общее состояние и базовые операции всех калькуляторов."""

    def __init__(self) -> None:
        """Создаёт начальное состояние калькулятора."""
        # Выражение хранится по отдельным элементам, чтобы редактировать текущий операнд.
        self.tokens: list[str] = []
        self.display = "0"
        self.expression = ""
        self.replace_display = True
        self.error = False
        self.finished = False
        self.last_operator: str | None = None
        self.last_operand: float | None = None
        self.angle_mode = "DEG"
        self.history: list[tuple[str, str]] = []

    def enter_digit(self, digit: str) -> None:
        """Добавляет цифру к текущему числу или начинает новое число."""
        if self.error or self.finished:
            self.clear()
        # После закрывающей скобки новое число неявно умножается на её результат.
        if self.tokens and self.tokens[-1] == ")":
            self.tokens.append("*")
            self.replace_display = True
        if self.replace_display:
            self.display = digit
            self.replace_display = False
            self._update_operand()
        elif len(self.display) < 16:
            self.display = digit if self.display == "0" else self.display + digit
            self._update_operand()

    def enter_decimal(self) -> None:
        """Добавляет десятичную точку к текущему числу."""
        if self.error or self.finished:
            self.clear()
        # Новое дробное число начинается с нуля перед точкой.
        if self.tokens and self.tokens[-1] == ")":
            self.tokens.append("*")
            self.replace_display = True
        if self.replace_display:
            self.display = "0."
            self.replace_display = False
            self._update_operand()
        elif "." not in self.display:
            self.display += "."
            self._update_operand()

    def set_operator(self, operator_name: str) -> None:
        """Добавляет оператор или заменяет последний ожидающий оператор."""
        if operator_name not in OPERATORS:
            raise ValueError(f"Unknown operator: {operator_name}")
        if self.error:
            self.clear()
        if self.finished:
            self.tokens = [self.display]
            self.finished = False
        # Два оператора подряд заменяют друг друга; после "(" нужен операнд.
        if not self.tokens:
            self.tokens.append(self.display)
        if self.tokens[-1] in OPERATORS:
            self.tokens[-1] = operator_name
        elif self.tokens[-1] == "(":
            return
        else:
            self.tokens.append(operator_name)
        self.replace_display = True
        self.last_operator = None
        self.last_operand = None
        self._refresh_expression()

    def enter_parenthesis(self, parenthesis: str) -> None:
        """Добавляет открывающую или закрывающую скобку."""
        if parenthesis not in ("(", ")"):
            raise ValueError(f"Unknown parenthesis: {parenthesis}")
        if self.error:
            self.clear()
        if self.finished:
            self.clear()
        if parenthesis == "(":
            # Между числом или закрывающей скобкой и "(" подразумевается умножение.
            if self.tokens and self.tokens[-1] not in OPERATORS and self.tokens[-1] != "(":
                self.tokens.append("*")
            self.tokens.append("(")
            self.replace_display = True
        elif (
            self.tokens
            and self.tokens.count("(") > self.tokens.count(")")
            and self.tokens[-1] not in OPERATORS
            and self.tokens[-1] != "("
        ):
            self.tokens.append(")")
            self.replace_display = True
        else:
            # Лишняя закрывающая скобка или пустая группа не образуют выражение.
            self._set_error()
            return
        self._refresh_expression()

    def equals(self) -> None:
        """Вычисляет выражение или повторяет последнюю бинарную операцию."""
        if self.error:
            return
        if self.finished:
            # Повтор "=" применяет последнюю операцию к результату.
            if self.last_operator is not None and self.last_operand is not None:
                try:
                    result = OPERATORS[self.last_operator](float(self.display), self.last_operand)
                    self.display = self._format(result)
                except (ArithmeticError, ValueError):
                    self._set_error()
            return
        if not self.tokens:
            return
        tokens = self.tokens.copy()
        if tokens[-1] in OPERATORS:
            # Для «5 + =» используем текущий операнд повторно.
            tokens.append(self.display)
        expression_text = " ".join(SYMBOLS.get(token, token) for token in tokens)
        try:
            tree = ast.parse(" ".join(tokens), mode="eval").body
            result = self._evaluate(tree)
            formatted = self._format(result)
            if isinstance(tree, ast.BinOp):
                op = self._operator_from_node(tree.op)
                operand = self._evaluate(tree.right)
            else:
                op = None
                operand = None
        except (SyntaxError, ArithmeticError, ValueError, RecursionError):
            self._set_error()
            return
        self.tokens = tokens
        self._refresh_expression()
        self.display = formatted
        self.last_operator = op
        self.last_operand = operand
        self.finished = True
        self.replace_display = True
        self.history.append((expression_text, formatted))

    def percent(self) -> None:
        """Преобразует текущий операнд в процент."""
        if self.error:
            return
        try:
            value = self._operand_value()
            start = self._operand_start()
            # Для сложения и вычитания процент берётся от предшествующего выражения.
            if start > 0 and self.tokens[start - 1] in ("+", "-"):
                base_tokens = self.tokens[:start - 1]
                balance = base_tokens.count("(") - base_tokens.count(")")
                base_tokens += [")"] * balance
                value *= self._evaluate(ast.parse(" ".join(base_tokens), mode="eval").body)
            self._set_operand(value / 100)
        except (SyntaxError, ArithmeticError, ValueError, RecursionError):
            self._set_error()

    def toggle_sign(self) -> None:
        """Меняет знак текущего числа или выражения в скобках."""
        if self.error:
            return
        try:
            # Закрытая группа рассматривается как единый операнд.
            self._set_operand(-self._operand_value(), editable=True)
        except (SyntaxError, ArithmeticError, ValueError, RecursionError):
            self._set_error()

    def backspace(self) -> None:
        """Удаляет последний символ текущего числа."""
        if self.error:
            self.clear()
        elif not self.replace_display:
            # На дисплее не остаётся пустая строка или один знак минуса.
            self.display = self.display[:-1] or "0"
            if self.display == "-":
                self.display = "0"
            self._update_operand()

    def clear_entry(self) -> None:
        """Очищает текущий операнд, сохраняя выражение."""
        if self.error:
            self.clear()
            return
        # После результата CE начинает новое выражение с нуля.
        if self.finished:
            self.clear()
            return
        self._set_operand(0)

    def clear(self) -> None:
        """Сбрасывает выражение, результат и состояние ошибки."""
        # Повторное нажатие "=" больше не использует предыдущее вычисление.
        self.tokens = []
        self.display = "0"
        self.expression = ""
        self.replace_display = True
        self.error = False
        self.finished = False
        self.last_operator = None
        self.last_operand = None

    def clear_history(self) -> None:
        """Очищает историю, не изменяя текущее вычисление."""
        self.history.clear()

    def _update_operand(self) -> None:
        """Добавляет или заменяет редактируемый числовой операнд."""
        # Операторы и скобки отделены от чисел в списке элементов.
        if not self.tokens or self.tokens[-1] in OPERATORS or self.tokens[-1] == "(":
            self.tokens.append(self.display)
        else:
            self.tokens[-1] = self.display
        self._refresh_expression()

    def _operand_start(self) -> int:
        """Возвращает индекс начала последнего операнда."""
        if not self.tokens or self.tokens[-1] != ")":
            return max(0, len(self.tokens) - 1)
        # При вложенных скобках ищем соответствующую открывающую скобку.
        depth = 0
        for index in range(len(self.tokens) - 1, -1, -1):
            if self.tokens[index] == ")":
                depth += 1
            elif self.tokens[index] == "(":
                depth -= 1
                if depth == 0:
                    return index - 1 if index > 0 and self.tokens[index - 1] in FUNCTIONS else index
        raise ValueError("Unmatched parenthesis")

    def _operand_value(self) -> float:
        """Возвращает значение текущего числа или группы в скобках."""
        # В завершённом выражении текущим операндом является показанный результат.
        if self.finished or not self.tokens or self.tokens[-1] != ")":
            return float(self.display)
        return self._evaluate(ast.parse(" ".join(self.tokens[self._operand_start():]), mode="eval").body)

    def _set_operand(self, value: float, editable: bool = False) -> None:
        """Заменяет текущий операнд вычисленным значением."""
        formatted = self._format(value)
        if self.finished:
            self.tokens = []
            self.finished = False
        # Группа в скобках заменяется целиком, а ожидающий оператор сохраняется.
        if self.tokens and self.tokens[-1] not in OPERATORS and self.tokens[-1] != "(":
            del self.tokens[self._operand_start():]
        self.display = formatted
        self.tokens.append(formatted)
        self.replace_display = not editable
        self._refresh_expression()

    def _refresh_expression(self) -> None:
        """Обновляет строку выражения для интерфейса."""
        # Внутренние операторы заменяются на удобные для отображения символы.
        self.expression = " ".join(SYMBOLS.get(token, token) for token in self.tokens)

    @staticmethod
    def _operator_from_node(node: ast.operator) -> str:
        """Возвращает строковый оператор для поддерживаемого узла AST."""
        # Возведение в степень не вводится отдельным оператором, чтобы сохранить
        # совместимость с простым текстовым синтаксисом калькулятора.
        mapping = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Pow: "**",
        }
        if type(node) not in mapping:
            raise ValueError("Unsupported operator")
        return mapping[type(node)]

    def _evaluate(self, node: ast.AST) -> float:
        """Вычисляет только числа и разрешённые арифметические узлы AST."""
        # AST обеспечивает приоритет и скобки без исполнения произвольного кода.
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = self._evaluate(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            return OPERATORS[self._operator_from_node(node.op)](
                self._evaluate(node.left), self._evaluate(node.right)
            )
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in FUNCTIONS
            and len(node.args) == 1
            and not node.keywords
        ):
            return self._apply_function(node.func.id, self._evaluate(node.args[0]))
        raise ValueError("Unsupported expression")

    def _set_error(self) -> None:
        """Переводит калькулятор в состояние ошибки."""
        # Ошибка остаётся видимой до начала нового ввода или сброса.
        self.display = "Невозможно"
        self.error = True
        self.replace_display = True
        self.finished = False
        self.last_operator = None
        self.last_operand = None

    @staticmethod
    def _format(value: float) -> str:
        """Форматирует конечное число для дисплея."""
        # Бесконечность и NaN показываются как ошибка, а не как числовой результат.
        if not math.isfinite(value):
            raise ValueError("Non-finite result")
        return f"{value:.12g}"
