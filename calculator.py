import tkinter as tk

from calculator_ui import CalculatorApp


def main() -> None:
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
