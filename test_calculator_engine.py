import math
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from calculator_engine import Calculator
from calculator_ui import CalculatorApp


class CalculatorChainedOperationsTests(unittest.TestCase):
    def test_chains_operations_before_equals(self) -> None:
        """Проверяет последовательный ввод операций без промежуточного "="."""
        calculator = Calculator()
        # Операции одинакового приоритета выполняются слева направо.
        for key in ("5", "+", "6", "-", "7", "="):
            if key.isdigit():
                calculator.enter_digit(key)
            elif key == "=":
                calculator.equals()
            else:
                calculator.set_operator(key)

        self.assertEqual(calculator.display, "4")
        self.assertEqual(calculator.expression, "5 + 6 − 7")

    def test_precedence_and_parentheses(self) -> None:
        """Проверяет приоритет операторов, скобки и их вложенность."""
        # Проверяем также левую ассоциативность умножения и деления.
        cases = {
            "2+3*4=": "14",
            "(2+3)*4=": "20",
            "2*(3+(4*5))=": "46",
            "20/5*2=": "8",
            "2(3+4)=": "14",
            "(2+3)(4+1)=": "25",
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                calculator = Calculator()
                for key in expression:
                    if key.isdigit():
                        calculator.enter_digit(key)
                    elif key in "+-*/":
                        calculator.set_operator(key)
                    elif key in "()":
                        calculator.enter_parenthesis(key)
                    else:
                        calculator.equals()
                self.assertEqual(calculator.display, expected)

    def test_invalid_expression_and_division_by_zero(self) -> None:
        """Показывает ошибку при неверных скобках и делении на ноль."""
        # После ошибки новый ввод начинает новое вычисление.
        calculator = Calculator()
        calculator.enter_parenthesis(")")
        self.assertTrue(calculator.error)
        calculator.clear()
        calculator.enter_parenthesis("(")
        calculator.enter_parenthesis(")")
        self.assertTrue(calculator.error)
        calculator.clear()
        calculator.enter_parenthesis("(")
        calculator.enter_digit("2")
        calculator.equals()
        self.assertTrue(calculator.error)
        calculator.enter_digit("8")
        calculator.set_operator("/")
        calculator.enter_digit("0")
        calculator.equals()
        self.assertTrue(calculator.error)
        calculator.enter_digit("3")
        self.assertEqual(calculator.display, "3")
        self.assertFalse(calculator.error)

    def test_percent_unary_and_repeated_equals(self) -> None:
        """Сохраняет работу процентов, унарных операций и повторного равенства."""
        # 200 + 10% равно 220; повторное равенство снова прибавляет 20.
        calculator = Calculator()
        for digit in "200":
            calculator.enter_digit(digit)
        calculator.set_operator("+")
        for digit in "10":
            calculator.enter_digit(digit)
        calculator.percent()
        calculator.equals()
        self.assertEqual(calculator.display, "220")
        calculator.equals()
        self.assertEqual(calculator.display, "240")
        calculator.clear()
        calculator.enter_digit("2")
        calculator.set_operator("+")
        calculator.enter_digit("3")
        calculator.unary("square")
        calculator.equals()
        self.assertEqual(calculator.display, "11")
        # Унарная операция после закрывающей скобки применяется ко всей группе.
        calculator.clear()
        calculator.enter_digit("2")
        calculator.set_operator("*")
        calculator.enter_parenthesis("(")
        calculator.enter_digit("3")
        calculator.set_operator("+")
        calculator.enter_digit("1")
        calculator.enter_parenthesis(")")
        calculator.unary("square")
        calculator.equals()
        self.assertEqual(calculator.display, "32")

    def test_engineering_operations_and_constants(self) -> None:
        """Проверяет инженерные функции и ошибки за пределами их математического домена."""
        cases = {
            "sin": ("0", "0"),
            "square": ("3", "9"),
            "cube": ("2", "8"),
            "log10": ("100", "2"),
            "factorial": ("5", "120"),
        }
        for operation, (value, expected) in cases.items():
            with self.subTest(operation=operation):
                calculator = Calculator()
                calculator.enter_digit(value)
                calculator.unary(operation)
                self.assertEqual(calculator.display, expected)

        calculator = Calculator()
        calculator.constant("pi")
        self.assertEqual(calculator.display, "3.14159265359")
        calculator.clear()
        calculator.enter_digit("0")
        calculator.unary("ln")
        self.assertTrue(calculator.error)

    def test_function_uses_full_expression_as_argument(self) -> None:
        """Проверяет порядок вычисления cos(5*8)+5."""
        calculator = Calculator()
        calculator.enter_function("cos")
        for key in ("5", "*", "8", ")", "+", "5"):
            if key.isdigit():
                calculator.enter_digit(key)
            elif key in "+-*/":
                calculator.set_operator(key)
            else:
                calculator.enter_parenthesis(key)
        calculator.equals()
        self.assertAlmostEqual(
            float(calculator.display), math.cos(math.radians(40)) + 5, places=10
        )

        calculator.toggle_angle_mode()
        self.assertEqual(calculator.angle_mode, "RAD")

    def test_graph_expression_supports_x_and_functions(self) -> None:
        """Проверяет безопасное вычисление функций графика для значения x."""
        calculator = Calculator()
        self.assertEqual(calculator.evaluate_graph("x^2 + 2*x", 3), 15)
        self.assertAlmostEqual(
            calculator.evaluate_graph("cos(5*8)+5", 0),
            math.cos(math.radians(40)) + 5,
            places=10,
        )

    def test_keyboard_parentheses(self) -> None:
        """Передаёт клавиши скобок в общий обработчик действий."""
        # Проверка не создаёт окно Tkinter и работает без графического окружения.
        app = CalculatorApp.__new__(CalculatorApp)
        app._press = Mock()
        for char in "()":
            self.assertEqual(app._on_key(SimpleNamespace(char=char, keysym=char)), "break")
            app._press.assert_called_with(char)


if __name__ == "__main__":
    unittest.main()
