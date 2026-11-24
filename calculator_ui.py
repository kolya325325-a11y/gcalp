import tkinter as tk
import sys

from calculator_engine import Calculator


# Платформо-зависимая палитра для корректной отрисовки на разных ОС
IS_MAC = sys.platform == "darwin"

BACKGROUND = "#202020"
# На Mac используются более светлые цвета для лучшей видимости
BUTTON = "#323232" if not IS_MAC else "#424242"
BUTTON_HOVER = "#3d3d3d" if not IS_MAC else "#505050"
BUTTON_FUNCTION = "#292929" if not IS_MAC else "#353535"
ACCENT = "#4cc2ff" if not IS_MAC else "#2196F3"
TEXT = "#f4f4f4"
MUTED = "#a9a9a9"


class CalculatorApp:
    def __init__(self, root: tk.Tk) -> None:
        """Создаёт интерфейс и связывает его с вычислительной моделью."""
        self.root = root
        # Интерфейс отображает состояние модели, но не выполняет арифметику сам.
        self.calculator = Calculator()
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.mode = tk.StringVar(value="Стандартный")
        self._configure_window()
        self._create_widgets()
        self._bind_keyboard()

    def _configure_window(self) -> None:
        """Настраивает заголовок, фон, размер и шрифты окна."""
        # Используйте системный шрифт для каждой платформы (Mac, Windows, Linux)
        font_family = "Helvetica" if IS_MAC else "Segoe UI"
        self.root.title("Калькулятор")
        self.root.configure(bg=BACKGROUND)
        self.root.geometry("360x620")
        self.root.minsize(320, 550)
        self.root.option_add("*Font", (font_family, 11))

    def _create_widgets(self) -> None:
        """Создаёт панели дисплея и сетку кнопок калькулятора."""
        top = tk.Frame(self.root, bg=BACKGROUND, padx=14, pady=10)
        top.pack(fill="x")

        menu_button = tk.Button(
            top, text="☰", command=self._show_mode_menu, bg=BACKGROUND,
            fg=TEXT, activebackground=BUTTON_HOVER, activeforeground=TEXT,
            relief="flat", bd=0, font=("Segoe UI", 16), cursor="hand2",
            takefocus=False,
        )
        menu_button.pack(side="left", padx=(2, 14))
        tk.Label(
            top, textvariable=self.mode, bg=BACKGROUND, fg=TEXT,
            font=("Segoe UI Semibold", 12),
        ).pack(side="left")

        display = tk.Frame(self.root, bg=BACKGROUND, padx=18, pady=8)
        display.pack(fill="x", expand=True)
        # Выражение показывается над результатом, как в стандартном калькуляторе Windows.
        tk.Label(
            display, text="Калькулятор", bg=BACKGROUND, fg=TEXT,
            anchor="w", font=("Segoe UI Semibold", 16),
        ).pack(fill="x", pady=(0, 20))
        tk.Label(
            display, textvariable=self.expression, bg=BACKGROUND, fg=MUTED,
            anchor="e", font=("Segoe UI", 12), height=1,
        ).pack(fill="x", pady=(0, 4))

        self.result_label = tk.Label(
            display, textvariable=self.result, bg=BACKGROUND, fg=TEXT,
            anchor="e", font=("Segoe UI Light", 36), height=1,
        )
        self.result_label.pack(fill="x")
        display.bind("<Configure>", self._fit_result)

        self.grid = tk.Frame(self.root, bg=BACKGROUND, padx=8, pady=8)
        self.grid.pack(fill="both", expand=True)
        self._render_keys()

    def _render_keys(self) -> None:
        """Перестраивает сетку кнопок для выбранного режима."""
        self.angle_button = None
        for child in self.grid.winfo_children():
            child.destroy()

        engineering = self.mode.get() == "Инженерный"
        columns = 6 if engineering else 4
        for column in range(columns):
            self.grid.columnconfigure(column, weight=1, uniform="calculator")
        for row in range(8 if engineering else 7):
            self.grid.rowconfigure(row, weight=1, uniform="calculator")

        if not engineering:
            self._make_button(self.grid, "(", "(", 0, 0, columnspan=2)
            self._make_button(self.grid, ")", ")", 0, 2, columnspan=2)
            keys = (
                (("%", "percent"), ("CE", "clear_entry"), ("C", "clear"), ("⌫", "backspace")),
                (("1/x", "reciprocal"), ("x²", "square"), ("√x", "sqrt"), ("÷", "/")),
                (("7", "7"), ("8", "8"), ("9", "9"), ("×", "*")),
                (("4", "4"), ("5", "5"), ("6", "6"), ("−", "-")),
                (("1", "1"), ("2", "2"), ("3", "3"), ("+", "+")),
                (("+/−", "sign"), ("0", "0"), (".", "decimal"), ("=", "equals")),
            )
            row_offset = 1
        else:
            keys = (
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
            row_offset = 0

        for row, key_row in enumerate(keys):
            column = 0
            for label, action in key_row:
                self._make_button(
                    self.grid, label, action, row + row_offset, column,
                )
                column += 1

    def _show_mode_menu(self) -> None:
        """Показывает меню переключения между стандартным и инженерным режимами."""
        menu = tk.Menu(
            self.root, tearoff=False, bg=BUTTON_FUNCTION, fg=TEXT,
            activebackground=BUTTON_HOVER, activeforeground=TEXT,
        )
        menu.add_command(label="Стандартный", command=lambda: self._set_mode("Стандартный"))
        menu.add_command(label="Инженерный", command=lambda: self._set_mode("Инженерный"))
        menu.post(self.root.winfo_rootx() + 14, self.root.winfo_rooty() + 42)

    def _set_mode(self, mode: str) -> None:
        """Переключает раскладку и сохраняет текущее состояние вычисления."""
        if mode not in ("Стандартный", "Инженерный"):
            raise ValueError(f"Unknown calculator mode: {mode}")
        self.mode.set(mode)
        self.root.minsize(320, 550 if mode == "Стандартный" else 650)
        self._render_keys()

    def _make_button(
        self, parent: tk.Frame, label: str, action: str, row: int, column: int,
        columnspan: int = 1,
    ) -> None:
        """Создаёт и размещает одну кнопку с её визуальным оформлением."""
        # Цифровые клавиши и "=" выделяются цветом, функциональные остаются темнее.
        is_number = action.isdigit() or action in ("decimal", "sign")
        is_equals = action == "equals"
        color = ACCENT if is_equals else (BUTTON if is_number else BUTTON_FUNCTION)
        # На Mac используйте более темный текст для кнопки "=" для лучшей контрастности
        foreground = "#1a1a1a" if is_equals else TEXT
        button = tk.Button(
            parent,
            text=label,
            command=lambda: self._press(action),
            bg=color,
            fg=foreground,
            activebackground=BUTTON_HOVER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI Semibold" if is_equals else "Segoe UI", 14),
            cursor="hand2",
            takefocus=False,
        )
        if action == "toggle_angle":
            self.angle_button = button
        button.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=3, pady=3)
        if not is_equals:
            hover = BUTTON_HOVER if is_number else "#353535"
            # Значения по умолчанию сохраняют цвет и кнопку именно этой итерации.
            button.bind("<Enter>", lambda _event, b=button, c=hover: b.configure(bg=c))
            button.bind("<Leave>", lambda _event, b=button, c=color: b.configure(bg=c))

    def _bind_keyboard(self) -> None:
        """Подключает обработчик клавиатурного ввода ко всему окну."""
        # Общая привязка работает даже тогда, когда фокус не на отдельной кнопке.
        self.root.bind_all("<Key>", self._on_key)

    def _on_key(self, event: tk.Event) -> str | None:
        """Преобразует нажатие клавиши в действие калькулятора."""
        char = event.char
        key = event.keysym
        # Клавиатурный ввод использует те же действия, что и кнопки интерфейса.
        if char in "0123456789" and char:
            self._press(char)
        elif char in "+-*/%" and char:
            self._press("%" if char == "%" else char)
        elif char in "()" and char:
            self._press(char)
        elif char == "." or key == "KP_Decimal":
            self._press("decimal")
        elif key in ("Return", "KP_Enter", "equal"):
            self._press("equals")
        elif key == "BackSpace":
            self._press("backspace")
        elif key == "Escape":
            self._press("clear")
        elif key == "Delete":
            self._press("clear_entry")
        else:
            return None
        # Не даём Tkinter обработать распознанное нажатие повторно.
        return "break"

    def _press(self, action: str) -> None:
        """Передаёт действие вычислителю и обновляет виджеты."""
        # Все кнопки переводятся в команды модели, затем обновляется отображение.
        calculator = self.calculator
        if action.isdigit():
            calculator.enter_digit(action)
        elif action == "decimal":
            calculator.enter_decimal()
        elif action in ("+", "-", "*", "/"):
            calculator.set_operator(action)
        elif action in ("(", ")"):
            calculator.enter_parenthesis(action)
        elif action == "equals":
            calculator.equals()
        elif action == "percent":
            calculator.percent()
        elif action == "sign":
            calculator.toggle_sign()
        elif action == "toggle_angle":
            calculator.toggle_angle_mode()
        elif action.startswith("function_"):
            calculator.enter_function(action.removeprefix("function_"))
        elif action in ("reciprocal", "square", "sqrt"):
            calculator.unary(action)
        elif action in ("pi", "e"):
            calculator.constant(action)
        elif action == "backspace":
            calculator.backspace()
        elif action == "clear_entry":
            calculator.clear_entry()
        elif action == "clear":
            calculator.clear()
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Синхронизирует текст дисплея и цвет ошибки с состоянием модели."""
        calculator = self.calculator
        # StringVar синхронизирует текст виджетов с состоянием вычислителя.
        self.result.set(calculator.display)
        self.expression.set(calculator.expression)
        self.result_label.configure(
            fg="#ff6b6b" if calculator.error else TEXT
        )
        if self.angle_button is not None:
            self.angle_button.configure(text=calculator.angle_mode)

    def _fit_result(self, event: tk.Event) -> None:
        """Подбирает размер шрифта результата при изменении размера окна."""
        # Уменьшаем шрифт, чтобы длинный результат помещался в область дисплея.
        size = 36 if len(self.calculator.display) <= 10 else max(
            18, 360 // len(self.calculator.display)
        )
        self.result_label.configure(font=("Segoe UI Light", size))
