"""Раскладка инженерного калькулятора."""

ENGINEERING_KEYS = (
    (("sin", "function_sin"), ("cos", "function_cos"),
     ("tan", "function_tan"), ("ln", "function_ln"),
     ("log", "function_log10"), ("π", "pi")),
    (("sin⁻¹", "function_asin"), ("cos⁻¹", "function_acos"),
     ("tan⁻¹", "function_atan"), ("x²", "function_square"),
     ("x³", "function_cube"), ("e", "e")),
    (("√x", "function_sqrt"), ("1/x", "function_reciprocal"),
     ("|x|", "function_abs"), ("n!", "function_factorial"),
     ("10ˣ", "function_ten_power"), ("eˣ", "function_exp")),
    (("DEG", "toggle_angle"), ("%", "percent"), ("CE", "clear_entry"),
     ("C", "clear"), ("⌫", "backspace"), ("(", "(")),
    ((")", ")"), ("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/"), ("×", "*")),
    (("−", "-"), ("4", "4"), ("5", "5"), ("6", "6"), ("+", "+"), ("=", "equals")),
    (("1", "1"), ("2", "2"), ("3", "3"), ("0", "0"), (".", "decimal"),
     ("+/−", "sign")),
)

__all__ = ["ENGINEERING_KEYS"]
