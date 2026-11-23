import unittest

from calculator_engine import Calculator


class CalculatorChainedOperationsTests(unittest.TestCase):
    def test_chains_operations_before_equals(self) -> None:
        calculator = Calculator()
        for key in ("5", "+", "6", "-", "7", "="):
            if key.isdigit():
                calculator.enter_digit(key)
            elif key == "=":
                calculator.equals()
            else:
                calculator.set_operator(key)

        self.assertEqual(calculator.display, "4")
        self.assertEqual(calculator.expression, "5 + 6 − 7")


if __name__ == "__main__":
    unittest.main()
