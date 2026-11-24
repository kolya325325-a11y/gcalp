import ast
import io
import math
import operator
import tokenize


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
        self._editable_expression: str | None = None

    def set_expression(self, expression: str) -> None:
        """Заменяет всё выражение текстом, введённым или отредактированным в UI."""
        self._editable_expression = expression
        self.expression = expression
        self.error = False
        self.finished = False
        self.last_operator = None
        self.last_operand = None
        try:
            self.tokens = self._parse_expression(expression)
        except (SyntaxError, tokenize.TokenError, ValueError, RecursionError):
            self.tokens = []
            self.replace_display = True
            return
        try:
            tree = ast.parse(" ".join(self.tokens), mode="eval").body
            self.display = self._format(self._evaluate(tree))
            self.replace_display = False
        except (SyntaxError, tokenize.TokenError, ArithmeticError, ValueError, RecursionError):
            # Незавершённое выражение является допустимым состоянием во время
            # редактирования; ошибка показывается только при нажатии "=".
            numeric_tokens = [
                token for token in self.tokens
                if token.lstrip("+-").replace(".", "", 1).isdigit()
            ]
            if numeric_tokens:
                self.display = numeric_tokens[-1]
            self.replace_display = True

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
            if self._editable_expression is None:
                return
        if self._editable_expression is not None:
            try:
                self.tokens = self._parse_expression(self._editable_expression)
            except (SyntaxError, tokenize.TokenError, ValueError, RecursionError):
                self._set_error()
                return
            self._editable_expression = None
            self.finished = False
            self.error = False
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
        self._editable_expression = None

    def clear_history(self) -> None:
        """Очищает историю, не изменяя текущее вычисление."""
        # История очищается отдельно, чтобы текущий результат остался на экране.
        self.history.clear()

    @staticmethod
    def _parse_expression(expression: str) -> list[str]:
        """Безопасно разбирает текст UI в элементы выражения калькулятора."""
        normalized = (
            expression.replace("−", "-")
            .replace("×", "*")
            .replace("÷", "/")
            .replace("^", "**")
            .replace("π", "pi")
        )
        tokens: list[tuple[tokenize.TokenInfo, str]] = []
        try:
            for item in tokenize.generate_tokens(io.StringIO(normalized).readline):
                if item.type in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NEWLINE):
                    continue
                if item.type in (tokenize.INDENT, tokenize.DEDENT):
                    continue
                if item.type == tokenize.ERRORTOKEN and item.string.isspace():
                    continue
                if item.type not in (tokenize.NUMBER, tokenize.NAME, tokenize.OP):
                    raise ValueError("Unsupported expression token")
                if item.type == tokenize.NAME and item.string not in {
                    *FUNCTIONS,
                    "percent",
                    "pi",
                    "e",
                }:
                    raise ValueError("Unknown function or constant")
                if item.type == tokenize.OP and item.string not in (
                    "+", "-", "*", "/", "**", "%", "(", ")", ","
                ):
                    raise ValueError("Unsupported operator")
                tokens.append((item, item.string))
        except (IndentationError, tokenize.TokenError) as error:
            raise SyntaxError("Incomplete expression") from error

        result = BaseCalculator._expand_percent_tokens([value for _, value in tokens])
        expanded: list[tuple[tokenize.TokenInfo, str]] = []
        for index, value in enumerate(result):
            token_type = (
                tokenize.NAME
                if value.isidentifier()
                else tokenize.NUMBER
                if value[0].isdigit() or value[0] == "."
                else tokenize.OP
            )
            synthetic = tokenize.TokenInfo(token_type, value, (1, 0), (1, 0), "")
            expanded.append((synthetic, value))

        result = []
        for index, (item, value) in enumerate(expanded):
            if result and index > 0 and BaseCalculator._needs_implicit_multiplication(
                expanded[index - 1], (item, value)
            ):
                result.append("*")
            result.append(value)
        if not result:
            raise SyntaxError("Empty expression")
        return result

    @staticmethod
    def _expand_percent_tokens(tokens: list[str]) -> list[str]:
        """Преобразует постфиксный процент в безопасный вызов percent()."""
        while "%" in tokens:
            percent_index = tokens.index("%")
            if percent_index == 0:
                raise SyntaxError("Percent without operand")
            start = percent_index - 1
            if tokens[start] == ")":
                depth = 1
                start -= 1
                while start >= 0 and depth:
                    if tokens[start] == ")":
                        depth += 1
                    elif tokens[start] == "(":
                        depth -= 1
                    start -= 1
                start += 1
                if start > 0 and tokens[start - 1] in FUNCTIONS:
                    start -= 1
            elif tokens[start] not in OPERATORS and tokens[start] not in ("(", ","):
                start = percent_index - 1
            else:
                raise SyntaxError("Percent without operand")

            operand = tokens[start:percent_index]
            base_operator = start - 1
            replacement = ["percent", "(", *operand]
            if base_operator >= 0 and tokens[base_operator] in ("+", "-"):
                base_start = BaseCalculator._percent_base_start(tokens, base_operator)
                base = tokens[base_start:base_operator]
                replacement.extend((",", "(", *base, ")"))
            replacement.append(")")
            tokens[start:percent_index + 1] = replacement
        return tokens

    @staticmethod
    def _percent_base_start(tokens: list[str], operator_index: int) -> int:
        """Находит начало базы процента в ближайшей незакрытой группе."""
        depth = 0
        for index in range(operator_index - 1, -1, -1):
            if tokens[index] == ")":
                depth += 1
            elif tokens[index] == "(":
                if depth == 0:
                    return index + 1
                depth -= 1
        return 0

    @staticmethod
    def _needs_implicit_multiplication(
        previous: tuple[tokenize.TokenInfo, str],
        current: tuple[tokenize.TokenInfo, str],
    ) -> bool:
        """Определяет неявное умножение, например 2(3) или 2π."""
        previous_type, previous_value = previous[0].type, previous[1]
        current_type, current_value = current[0].type, current[1]
        previous_is_constant = (
            previous_type == tokenize.NAME and previous_value in ("pi", "e")
        )
        current_is_constant = (
            current_type == tokenize.NAME and current_value in ("pi", "e")
        )
        current_is_function = (
            current_type == tokenize.NAME and current_value in FUNCTIONS
        )

        return (
            previous_type == tokenize.NUMBER
            and (current_value == "(" or current_is_constant or current_is_function)
        ) or (
            previous_value == ")"
            and (
                current_type == tokenize.NUMBER
                or current_value == "("
                or current_type == tokenize.NAME
            )
        ) or (
            previous_is_constant
            and (
                current_type == tokenize.NUMBER
                or current_value == "("
                or current_is_constant
                or current_is_function
            )
        )

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
        self._editable_expression = None
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
        if isinstance(node, ast.Name) and node.id in ("pi", "e"):
            return math.pi if node.id == "pi" else math.e
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
            and node.func.id == "percent"
            and len(node.args) in (1, 2)
            and not node.keywords
        ):
            value = self._evaluate(node.args[0]) / 100
            return value * self._evaluate(node.args[1]) if len(node.args) == 2 else value
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
