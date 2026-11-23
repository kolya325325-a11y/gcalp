import tkinter as tk

from calculator_ui import CalculatorApp


def main() -> None:
    """Создаёт окно приложения и запускает цикл обработки событий."""
    # Tkinter обслуживает нажатия кнопок и клавиш в главном цикле.
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
