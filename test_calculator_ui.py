import tkinter as tk
import unittest
from tkinter import ttk
from types import SimpleNamespace
from unittest.mock import Mock, patch

from calculator_engine import GraphingCalculator
from calculator_ui.common import CalculatorApp
from calculator_ui.graphing import draw_graph


class MacButtonTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk display unavailable: {error}")
        self.addCleanup(self.root.destroy)
        self.root.withdraw()
        self.mac = patch("calculator_ui.common.IS_MAC", True)
        self.mac.start()
        self.addCleanup(self.mac.stop)
        self.app = CalculatorApp(self.root)

    def test_buttons_work_in_all_modes_and_history(self) -> None:
        def find_button(parent: tk.Misc, text: str) -> ttk.Button:
            for child in parent.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == text:
                    return child
                try:
                    return find_button(child, text)
                except LookupError:
                    pass
            raise LookupError(text)

        find_button(self.app.grid, "7").invoke()
        self.assertEqual(self.app.calculator.display, "7")
        self.app._set_mode("Инженерный")
        self.assertIsInstance(find_button(self.app.grid, "sin"), ttk.Button)
        self.app._set_mode("Графический")
        find_button(self.app.graph_frame, "+ Добавить график").invoke()
        self.assertEqual(len(self.app.graph_expressions), 2)
        self.app._show_history()
        self.assertIsNotNone(self.app.history_window)
        find_button(self.app.history_window, "Очистить историю").invoke()
        self.app._set_mode("Стандартный")
        self.assertIsInstance(find_button(self.app.grid, "="), ttk.Button)

    def test_button_colors_and_system_menu(self) -> None:
        style = ttk.Style(self.root)
        self.assertEqual(style.theme_use(), "clam")
        for key, name in self.app._button_styles.items():
            background, foreground, active_background, active_foreground = key[:4]
            self.assertEqual(style.lookup(name, "background"), background)
            self.assertEqual(style.lookup(name, "foreground"), foreground)
            self.assertEqual(style.lookup(name, "background", ("active",)), active_background)
            self.assertEqual(style.lookup(name, "foreground", ("active",)), active_foreground)
        with patch("calculator_ui.common.tk.Menu") as menu:
            self.app._show_mode_menu()
        self.assertEqual(menu.call_args.kwargs, {"tearoff": False})
        self.assertEqual(menu.return_value.add_command.call_count, 3)

    def test_graph_backspace_deletes_character_before_cursor(self) -> None:
        entry = self.app.graph_active_entry
        self.assertIsNotNone(entry)
        entry.icursor(3)

        self.app._backspace_graph_text()

        self.assertEqual(entry.get(), "si(x)")
        self.assertEqual(entry.index(tk.INSERT), 2)


class GraphDrawingTests(unittest.TestCase):
    def test_sqrt_graph_skips_out_of_domain_samples(self) -> None:
        canvas = Mock()
        canvas.winfo_width.return_value = 400
        canvas.winfo_height.return_value = 300
        expression = Mock()
        expression.get.return_value = "sprt(x)"
        app = SimpleNamespace(
            graph_canvas=canvas,
            graph_x_min=-10.0,
            graph_x_max=10.0,
            graph_y_min=-10.0,
            graph_y_max=10.0,
            graph_expressions=[expression],
            calculator=GraphingCalculator(),
            graph_status=Mock(),
            _graph_tick_step=lambda _span: 5.0,
            _format_tick=str,
        )

        draw_graph(app)

        app.graph_status.set.assert_called_once_with("Построено графиков: 1")


class OtherPlatformButtonTests(unittest.TestCase):
    def test_uses_tk_button(self) -> None:
        app = CalculatorApp.__new__(CalculatorApp)
        parent = Mock(spec=tk.Misc)
        with patch("calculator_ui.common.IS_MAC", False), \
                patch("calculator_ui.common.tk.Button") as button:
            app._button(parent, text="7")
        button.assert_called_once_with(parent, text="7")


if __name__ == "__main__":
    unittest.main()
