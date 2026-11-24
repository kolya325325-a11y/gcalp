import tkinter as tk
import sys
from pathlib import Path

from calculator_ui import CalculatorApp


def main() -> None:
    """Создаёт окно приложения и запускает цикл обработки событий."""
    # Tkinter обслуживает нажатия кнопок и клавиш в главном цикле.
    root = tk.Tk()
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    icon = tk.PhotoImage(file=str(base_dir / "assets" / "calculator.png"))
    root.iconphoto(True, icon)
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
