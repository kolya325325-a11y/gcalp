import tkinter as tk

from calculator_engine import Calculator


# Палитра вынесена отдельно, чтобы оформление было легко менять целиком.
BACKGROUND = "#202020"
BUTTON = "#323232"
BUTTON_HOVER = "#3d3d3d"
BUTTON_FUNCTION = "#292929"
ACCENT = "#4cc2ff"
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
        self._configure_window()
        self._create_widgets()
        self._bind_keyboard()

    def _configure_window(self) -> None:
        """Настраивает заголовок, фон, размер и шрифты окна."""
        # Используется системный шрифт Windows, с которым интерфейс выглядит привычно.
        self.root.title("Калькулятор")
        self.root.configure(bg=BACKGROUND)
        self.root.geometry("360x570")
        self.root.minsize(320, 500)
        self.root.option_add("*Font", ("Segoe UI", 11))

    def _create_widgets(self) -> None:
        """Создаёт панели дисплея и сетку кнопок калькулятора."""
        # Верхняя панель содержит режим калькулятора, дисплей и сетку кнопок.
        top = tk.Frame(self.root, bg=BACKGROUND, padx=14, pady=10)
        top.pack(fill="x")

        tk.Label(
            top, text="☰", bg=BACKGROUND, fg=TEXT, font=("Segoe UI", 16)
        ).pack(side="left", padx=(2, 14))
        tk.Label(
            top, text="Стандартный", bg=BACKGROUND, fg=TEXT,
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

        grid = tk.Frame(self.root, bg=BACKGROUND, padx=8, pady=8)
        grid.pack(fill="both", expand=True)
        # Равномерные веса позволяют кнопкам растягиваться вместе с окном.
        for column in range(4):
            grid.columnconfigure(column, weight=1, uniform="calculator")
        for row in range(6):
            grid.rowconfigure(row, weight=1, uniform="calculator")

        # Подписи показываются пользователю, а action передаётся вычислительному модулю.
        keys = (
            (("%", "percent"), ("CE", "clear_entry"), ("C", "clear"), ("⌫", "backspace")),
            (("1/x", "reciprocal"), ("x²", "square"), ("√x", "sqrt"), ("÷", "/")),
            (("7", "7"), ("8", "8"), ("9", "9"), ("×", "*")),
            (("4", "4"), ("5", "5"), ("6", "6"), ("−", "-")),
            (("1", "1"), ("2", "2"), ("3", "3"), ("+", "+")),
            (("+/−", "sign"), ("0", "0"), (".", "decimal"), ("=", "equals")),
        )
        for row, key_row in enumerate(keys):
            for column, (label, action) in enumerate(key_row):
                self._make_button(grid, label, action, row, column)

    def _make_button(
        self, parent: tk.Frame, label: str, action: str, row: int, column: int
    ) -> None:
        """Создаёт и размещает одну кнопку с её визуальным оформлением."""
        # Цифровые клавиши и "=" выделяются цветом, функциональные остаются темнее.
        is_number = action.isdigit() or action in ("decimal", "sign")
        is_equals = action == "equals"
        color = ACCENT if is_equals else (BUTTON if is_number else BUTTON_FUNCTION)
        foreground = "#101010" if is_equals else TEXT
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
        button.grid(row=row, column=column, sticky="nsew", padx=3, pady=3)
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
        elif action == "equals":
            calculator.equals()
        elif action == "percent":
            calculator.percent()
        elif action == "sign":
            calculator.toggle_sign()
        elif action in ("reciprocal", "square", "sqrt"):
            calculator.unary(action)
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

    def _fit_result(self, event: tk.Event) -> None:
        """Подбирает размер шрифта результата при изменении размера окна."""
        # Уменьшаем шрифт, чтобы длинный результат помещался в область дисплея.
        size = 36 if len(self.calculator.display) <= 10 else max(
            18, 360 // len(self.calculator.display)
        )
        self.result_label.configure(font=("Segoe UI Light", size))
