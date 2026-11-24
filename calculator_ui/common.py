import tkinter as tk
import math
from tkinter import ttk
from typing import Any

from calculator_engine import GraphingCalculator
from .engineering import ENGINEERING_KEYS
from .graphing import (
    GRAPH_COLORS,
    GRAPH_FUNCTION_BUTTONS,
    GRAPH_NUMBER_BUTTONS,
    draw_graph,
)
from .standard import STANDARD_KEYS
from .theme import (
    ACCENT,
    BACKGROUND,
    BUTTON,
    BUTTON_FUNCTION,
    BUTTON_HOVER,
    IS_MAC,
    MUTED,
    TEXT,
)
class CalculatorApp:
    def __init__(self, root: tk.Tk) -> None:
        """Создаёт интерфейс и связывает его с вычислительной моделью."""
        self.root = root
        # Интерфейс отображает состояние модели, но не выполняет арифметику сам.
        self.calculator = GraphingCalculator()
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.mode = tk.StringVar(value="Стандартный")
        self.graph_expressions: list[tk.StringVar] = [
            tk.StringVar(value="sin(x)")
        ]
        self.graph_active_entry: tk.Entry | None = None
        self.graph_status = tk.StringVar()
        self.graph_x_min = -10.0
        self.graph_x_max = 10.0
        self.graph_y_min = -10.0
        self.graph_y_max = 10.0
        self.history_window: tk.Toplevel | None = None
        self._button_styles: dict[tuple, str] = {}
        if IS_MAC:
            self._button_style = ttk.Style(root)
            self._button_style.theme_use("clam")
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

        menu_button = self._button(
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
        self._button(
            top, text="История", command=self._show_history,
            bg=BACKGROUND, fg=MUTED, activebackground=BUTTON_HOVER,
            activeforeground=TEXT, relief="flat", bd=0,
            font=("Segoe UI", 10), cursor="hand2",
        ).pack(side="right")

        display = tk.Frame(self.root, bg=BACKGROUND, padx=18, pady=8)
        display.pack(fill="x", expand=True)
        self.display = display
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
        self._create_graph_view()
        self._render_keys()

    def _create_graph_view(self) -> None:
        """Создаёт панель графиков с выражением и координатной плоскостью."""
        self.graph_frame = tk.Frame(self.root, bg=BACKGROUND, padx=12, pady=10)

        self.graph_functions_frame = tk.Frame(self.graph_frame, bg=BACKGROUND)
        self.graph_functions_frame.pack(fill="x", pady=(0, 6))
        self._render_graph_functions()

        controls = tk.Frame(self.graph_frame, bg=BACKGROUND)
        controls.pack(fill="x", pady=(0, 8))
        self._button(
            controls, text="+ Добавить график", command=self._add_graph,
            bg=BUTTON_FUNCTION, fg=TEXT, activebackground=BUTTON_HOVER,
            relief="flat", bd=0, font=("Segoe UI", 11), cursor="hand2",
        ).pack(side="left", padx=(0, 5), ipadx=7, ipady=2)
        self._button(
            controls, text="Построить", command=self._plot_graph,
            bg=ACCENT, fg="#1a1a1a", activebackground=BUTTON_HOVER,
            relief="flat", bd=0, font=("Segoe UI Semibold", 11),
            cursor="hand2",
        ).pack(side="left", ipadx=8, ipady=4)

        function_buttons = tk.Frame(self.graph_frame, bg=BACKGROUND)
        function_buttons.pack(fill="x", pady=(0, 8))
        for label in GRAPH_FUNCTION_BUTTONS:
            self._button(
                function_buttons, text=label,
                command=lambda value=label: self._insert_graph_text(value),
                bg=BUTTON_FUNCTION, fg=TEXT, activebackground=BUTTON_HOVER,
                relief="flat", bd=0, font=("Segoe UI", 10), cursor="hand2",
            ).pack(side="left", padx=(0, 3), ipadx=4, ipady=1)

        number_buttons = tk.Frame(self.graph_frame, bg=BACKGROUND)
        number_buttons.pack(fill="x", pady=(0, 8))
        for label in GRAPH_NUMBER_BUTTONS:
            self._button(
                number_buttons, text=label,
                command=lambda value=label: self._insert_graph_text(value),
                bg=BUTTON, fg=TEXT, activebackground=BUTTON_HOVER,
                relief="flat", bd=0, font=("Segoe UI", 10), cursor="hand2",
            ).pack(side="left", padx=(0, 3), ipadx=7, ipady=1)
        self._button(
            number_buttons, text="⌫", command=self._backspace_graph_text,
            bg=BUTTON_FUNCTION, fg=TEXT, activebackground=BUTTON_HOVER,
            relief="flat", bd=0, font=("Segoe UI", 10), cursor="hand2",
        ).pack(side="left", padx=(0, 3), ipadx=7, ipady=1)

        toolbar = tk.Frame(self.graph_frame, bg=BACKGROUND)
        toolbar.pack(fill="x", pady=(0, 8))
        for label, command in (
            ("−", lambda: self._zoom_graph(1.25)),
            ("+", lambda: self._zoom_graph(0.8)),
            ("Сбросить вид", self._reset_graph_view),
        ):
            self._button(
                toolbar, text=label, command=command, bg=BUTTON_FUNCTION,
                fg=TEXT, activebackground=BUTTON_HOVER, relief="flat", bd=0,
                font=("Segoe UI", 11), cursor="hand2",
            ).pack(side="left", padx=(0, 5), ipadx=7, ipady=2)
        self.graph_angle_button = self._button(
            toolbar, text=self.calculator.angle_mode,
            command=self._toggle_graph_angle, bg=BUTTON_FUNCTION,
            fg=TEXT, activebackground=BUTTON_HOVER, relief="flat", bd=0,
            font=("Segoe UI", 11), cursor="hand2",
        )
        self.graph_angle_button.pack(side="left", ipadx=7, ipady=2)
        tk.Label(
            toolbar, textvariable=self.graph_status, bg=BACKGROUND, fg=MUTED,
            anchor="e",
        ).pack(side="right", fill="x", expand=True)

        self.graph_canvas = tk.Canvas(
            self.graph_frame, bg="#181818", highlightthickness=1,
            highlightbackground="#454545",
        )
        self.graph_canvas.pack(fill="both", expand=True)
        self.graph_canvas.bind("<Configure>", lambda _event: self._draw_graph())
        self.graph_canvas.bind("<ButtonPress-1>", self._start_graph_pan)
        self.graph_canvas.bind("<B1-Motion>", self._pan_graph)
        self.graph_canvas.bind("<MouseWheel>", self._on_graph_wheel)

    def _render_graph_functions(self) -> None:
        """Перестраивает строки выражений графиков."""
        for child in self.graph_functions_frame.winfo_children():
            child.destroy()
        for index, expression in enumerate(self.graph_expressions, start=1):
            row = tk.Frame(self.graph_functions_frame, bg=BACKGROUND)
            row.pack(fill="x", pady=2)
            color = GRAPH_COLORS[(index - 1) % len(GRAPH_COLORS)]
            tk.Label(
                row, text=f"f{index}(x) =", bg=BACKGROUND, fg=color,
                font=("Segoe UI Semibold", 11), width=7, anchor="w",
            ).pack(side="left")
            entry = tk.Entry(
                row, textvariable=expression, bg=BUTTON, fg=TEXT,
                insertbackground=TEXT, relief="flat", bd=0,
                font=("Segoe UI", 12),
            )
            entry.pack(side="left", fill="x", expand=True, ipady=5)
            entry.bind("<FocusIn>", lambda _event, widget=entry: self._set_graph_entry(widget))
            entry.bind("<Return>", lambda _event: self._plot_graph())
            if self.graph_active_entry is None and index == 1:
                self.graph_active_entry = entry
            if len(self.graph_expressions) > 1:
                self._button(
                    row, text="×",
                    command=lambda position=index - 1: self._remove_graph(position),
                    bg=BUTTON_FUNCTION, fg=TEXT, activebackground=BUTTON_HOVER,
                    relief="flat", bd=0, font=("Segoe UI", 11), cursor="hand2",
                ).pack(side="left", padx=(5, 0), ipadx=5, ipady=1)

    def _set_graph_entry(self, entry: tk.Entry) -> None:
        self.graph_active_entry = entry

    def _insert_graph_text(self, value: str) -> None:
        """Вставляет оператор или функцию в активную строку графика."""
        if self.graph_active_entry is None:
            return
        self.graph_active_entry.insert(tk.INSERT, value)
        self.graph_active_entry.focus_set()

    def _backspace_graph_text(self) -> None:
        """Удаляет символ перед курсором в активной строке графика."""
        if self.graph_active_entry is None:
            return
        cursor = self.graph_active_entry.index(tk.INSERT)
        if cursor > 0:
            self.graph_active_entry.delete(cursor - 1, cursor)
        self.graph_active_entry.focus_set()

    def _add_graph(self) -> None:
        """Добавляет вторую или следующую функцию на координатную плоскость."""
        self.graph_expressions.append(tk.StringVar(value="x^2"))
        self.graph_active_entry = None
        self._render_graph_functions()
        self._plot_graph()

    def _remove_graph(self, position: int) -> None:
        """Удаляет функцию, оставляя хотя бы одну строку для ввода."""
        if len(self.graph_expressions) <= 1:
            self.graph_expressions[0].set("")
        else:
            del self.graph_expressions[position]
        self.graph_active_entry = None
        self._render_graph_functions()
        self._plot_graph()

    def _plot_graph(self) -> None:
        """Строит текущую функцию и показывает ошибку некорректного ввода."""
        self._draw_graph()

    def _toggle_graph_angle(self) -> None:
        """Переключает градусы и радианы для тригонометрии на графике."""
        self.calculator.toggle_angle_mode()
        self.graph_angle_button.configure(text=self.calculator.angle_mode)
        self._draw_graph()

    def _draw_graph(self) -> None:
        """Перерисовывает сетку, оси и график функции."""
        if hasattr(self, "graph_canvas"):
            draw_graph(self)

    @staticmethod
    def _graph_tick_step(span: float) -> float:
        """Подбирает читаемый шаг подписей координат."""
        raw_step = span / 10
        exponent = math.floor(math.log10(raw_step))
        base = raw_step / (10**exponent)
        factor = 1 if base < 2 else 2 if base < 5 else 5
        return factor * (10**exponent)

    @staticmethod
    def _format_tick(value: float) -> str:
        return f"{value:.4g}"

    def _zoom_graph(self, factor: float) -> None:
        """Изменяет масштаб вокруг центра текущего вида."""
        x_center = (self.graph_x_min + self.graph_x_max) / 2
        y_center = (self.graph_y_min + self.graph_y_max) / 2
        x_half = (self.graph_x_max - self.graph_x_min) * factor / 2
        y_half = (self.graph_y_max - self.graph_y_min) * factor / 2
        self.graph_x_min, self.graph_x_max = x_center - x_half, x_center + x_half
        self.graph_y_min, self.graph_y_max = y_center - y_half, y_center + y_half
        self._draw_graph()

    def _reset_graph_view(self) -> None:
        self.graph_x_min, self.graph_x_max = -10.0, 10.0
        self.graph_y_min, self.graph_y_max = -10.0, 10.0
        self._draw_graph()

    def _start_graph_pan(self, event: tk.Event) -> None:
        self._graph_pan_origin = (event.x, event.y, self.graph_x_min, self.graph_y_min)

    def _pan_graph(self, event: tk.Event) -> None:
        if not hasattr(self, "_graph_pan_origin"):
            return
        start_x, start_y, x_min, y_min = self._graph_pan_origin
        width = max(1, self.graph_canvas.winfo_width())
        height = max(1, self.graph_canvas.winfo_height())
        dx = (event.x - start_x) / width * (self.graph_x_max - self.graph_x_min)
        dy = (event.y - start_y) / height * (self.graph_y_max - self.graph_y_min)
        x_span = self.graph_x_max - self.graph_x_min
        y_span = self.graph_y_max - self.graph_y_min
        self.graph_x_min, self.graph_x_max = x_min - dx, x_min - dx + x_span
        self.graph_y_min, self.graph_y_max = y_min + dy, y_min + dy + y_span
        self._draw_graph()

    def _on_graph_wheel(self, event: tk.Event) -> str:
        self._zoom_graph(0.8 if event.delta > 0 else 1.25)
        return "break"

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
            keys = STANDARD_KEYS
            row_offset = 1
        else:
            keys = ENGINEERING_KEYS
            row_offset = 0

        for row, key_row in enumerate(keys):
            column = 0
            for label, action in key_row:
                self._make_button(
                    self.grid, label, action, row + row_offset, column,
                )
                column += 1

    def _show_mode_menu(self) -> None:
        """Показывает меню переключения режимов."""
        menu_options = {} if IS_MAC else {
            "bg": BUTTON_FUNCTION, "fg": TEXT,
            "activebackground": BUTTON_HOVER, "activeforeground": TEXT,
        }
        menu = tk.Menu(self.root, tearoff=False, **menu_options)
        menu.add_command(label="Стандартный", command=lambda: self._set_mode("Стандартный"))
        menu.add_command(label="Инженерный", command=lambda: self._set_mode("Инженерный"))
        menu.add_command(label="Графический", command=lambda: self._set_mode("Графический"))
        menu.post(self.root.winfo_rootx() + 14, self.root.winfo_rooty() + 42)

    def _show_history(self) -> None:
        """Открывает окно истории вычислений."""
        if self.history_window is not None and self.history_window.winfo_exists():
            self._refresh_history_window()
            self.history_window.deiconify()
            self.history_window.lift()
            return

        window = tk.Toplevel(self.root)
        window.title("История вычислений")
        window.geometry("360x460")
        window.minsize(280, 260)
        window.configure(bg=BACKGROUND)
        window.protocol("WM_DELETE_WINDOW", window.withdraw)
        self.history_window = window

        tk.Label(
            window, text="История", bg=BACKGROUND, fg=TEXT,
            anchor="w", font=("Segoe UI Semibold", 14),
        ).pack(fill="x", padx=12, pady=(12, 6))
        list_frame = tk.Frame(window, bg=BACKGROUND)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.history_list = tk.Listbox(
            list_frame, bg=BUTTON, fg=TEXT, selectbackground=ACCENT,
            selectforeground="#1a1a1a", relief="flat", bd=0,
            yscrollcommand=scrollbar.set, font=("Segoe UI", 11),
        )
        self.history_list.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.history_list.yview)
        self._button(
            window, text="Очистить историю", command=self._clear_history,
            bg=BUTTON_FUNCTION, fg=TEXT, activebackground=BUTTON_HOVER,
            relief="flat", bd=0, font=("Segoe UI", 10), cursor="hand2",
        ).pack(fill="x", padx=12, pady=(0, 12), ipady=4)
        self._refresh_history_window()

    def _refresh_history_window(self) -> None:
        """Обновляет список истории, если окно открыто."""
        if (
            self.history_window is None
            or not self.history_window.winfo_exists()
            or not hasattr(self, "history_list")
        ):
            return
        self.history_list.delete(0, tk.END)
        if not self.calculator.history:
            self.history_list.insert(tk.END, "История пуста")
            return
        for expression, result in reversed(self.calculator.history):
            self.history_list.insert(tk.END, f"{expression} =")
            self.history_list.insert(tk.END, f"  {result}")

    def _clear_history(self) -> None:
        """Очищает историю вычислений."""
        self.calculator.clear_history()
        self._refresh_history_window()

    def _set_mode(self, mode: str) -> None:
        """Переключает раскладку и сохраняет текущее состояние вычисления."""
        if mode not in ("Стандартный", "Инженерный", "Графический"):
            raise ValueError(f"Unknown calculator mode: {mode}")
        self.mode.set(mode)
        if mode == "Графический":
            self.display.pack_forget()
            self.grid.pack_forget()
            self.graph_frame.pack(fill="both", expand=True)
            self.root.geometry("760x650")
            self.root.minsize(600, 500)
            self._draw_graph()
        else:
            self.graph_frame.pack_forget()
            self.display.pack(fill="x", expand=True)
            self.grid.pack(fill="both", expand=True)
            self.root.minsize(320, 550 if mode == "Стандартный" else 650)
            self._render_keys()

    def _button(self, parent: tk.Misc, **options: Any) -> tk.Button | ttk.Button:
        if not IS_MAC:
            return tk.Button(parent, **options)

        background = options.pop("bg")
        foreground = options.pop("fg")
        active_background = options.pop("activebackground")
        active_foreground = options.pop("activeforeground", TEXT)
        font = options.pop("font")
        options.pop("relief")
        options.pop("bd")
        key = (background, foreground, active_background, active_foreground, font)
        if key not in self._button_styles:
            style = f"Calculator{len(self._button_styles)}.TButton"
            self._button_style.configure(
                style, background=background, foreground=foreground,
                font=font, borderwidth=0, padding=0, width=0,
            )
            self._button_style.map(
                style,
                background=[("active", active_background)],
                foreground=[("active", active_foreground)],
            )
            self._button_styles[key] = style
        return ttk.Button(parent, style=self._button_styles[key], **options)

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
        button = self._button(
            parent,
            text=self.calculator.angle_mode if action == "toggle_angle" else label,
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
        if not is_equals and not IS_MAC:
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
            if self.mode.get() == "Стандартный":
                calculator.queue_percent()
            else:
                calculator.percent()
        elif action == "sign":
            calculator.toggle_sign()
        elif action == "toggle_angle":
            calculator.toggle_angle_mode()
        elif action.startswith("function_"):
            calculator.enter_function(action.removeprefix("function_"))
        elif action in ("reciprocal", "square", "sqrt"):
            if self.mode.get() == "Стандартный":
                calculator.queue_unary(action)
            else:
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
        self._refresh_history_window()

    def _fit_result(self, event: tk.Event) -> None:
        """Подбирает размер шрифта результата при изменении размера окна."""
        # Уменьшаем шрифт, чтобы длинный результат помещался в область дисплея.
        size = 36 if len(self.calculator.display) <= 10 else max(
            18, 360 // len(self.calculator.display)
        )
        self.result_label.configure(font=("Segoe UI Light", size))
