"""Общие настройки, кнопки и отрисовка графического калькулятора."""

import math

from .theme import ACCENT, MUTED

GRAPH_COLORS = ("#4cc2ff", "#ff9f43", "#a55eea", "#26de81", "#ff6b81")
GRAPH_FUNCTION_BUTTONS = (
    "sin(", "cos(", "tan(", "sqrt(", "ln(", "x", "^",
    "(", ")", "+", "−", "×", "÷",
)
GRAPH_NUMBER_BUTTONS = ("7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ".")


def draw_graph(app: object) -> None:
    """Рисует сетку и все функции через состояние графического представления."""
    canvas = app.graph_canvas
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width < 40 or height < 40:
        return
    canvas.delete("all")
    x_min, x_max = app.graph_x_min, app.graph_x_max
    y_min, y_max = app.graph_y_min, app.graph_y_max

    def to_pixel(x_value: float, y_value: float) -> tuple[float, float]:
        return (
            (x_value - x_min) / (x_max - x_min) * width,
            height - (y_value - y_min) / (y_max - y_min) * height,
        )

    step_x = app._graph_tick_step(x_max - x_min)
    step_y = app._graph_tick_step(y_max - y_min)
    first_x = math.ceil(x_min / step_x) * step_x
    first_y = math.ceil(y_min / step_y) * step_y
    tick = first_x
    while tick <= x_max + step_x / 2:
        px, _ = to_pixel(tick, 0)
        canvas.create_line(px, 0, px, height, fill="#2b2b2b")
        if abs(tick) > step_x / 100:
            canvas.create_text(
                px + 3, height - 12, text=app._format_tick(tick),
                fill=MUTED, anchor="w", font=("Segoe UI", 8),
            )
        tick += step_x
    tick = first_y
    while tick <= y_max + step_y / 2:
        _, py = to_pixel(0, tick)
        canvas.create_line(0, py, width, py, fill="#2b2b2b")
        if abs(tick) > step_y / 100:
            canvas.create_text(
                4, py - 3, text=app._format_tick(tick),
                fill=MUTED, anchor="w", font=("Segoe UI", 8),
            )
        tick += step_y

    if x_min <= 0 <= x_max:
        px, _ = to_pixel(0, 0)
        canvas.create_line(px, 0, px, height, fill="#8f8f8f", width=2)
    if y_min <= 0 <= y_max:
        _, py = to_pixel(0, 0)
        canvas.create_line(0, py, width, py, fill="#8f8f8f", width=2)

    expressions = [expression.get().strip() for expression in app.graph_expressions]
    if not any(expressions):
        app.graph_status.set("Добавьте функцию, например sin(x)")
        return
    samples = max(300, width)
    plotted = 0
    errors = 0
    for position, expression in enumerate(expressions):
        if not expression:
            continue
        color = GRAPH_COLORS[position % len(GRAPH_COLORS)]
        points: list[float] = []
        valid_samples = 0
        try:
            for index in range(samples + 1):
                x_value = x_min + (x_max - x_min) * index / samples
                try:
                    y_value = app.calculator.evaluate_graph(expression, x_value)
                except (ArithmeticError, ValueError, RecursionError):
                    if len(points) >= 4:
                        canvas.create_line(*points, fill=color, width=2, smooth=True)
                    points = []
                    continue
                valid_samples += 1
                if not math.isfinite(y_value) or abs(y_value) > (y_max - y_min) * 4:
                    if len(points) >= 4:
                        canvas.create_line(*points, fill=color, width=2, smooth=True)
                    points = []
                    continue
                px, py = to_pixel(x_value, y_value)
                points.extend((px, py))
            if len(points) >= 4:
                canvas.create_line(*points, fill=color, width=2, smooth=True)
            if valid_samples:
                plotted += 1
            else:
                errors += 1
        except (ArithmeticError, SyntaxError, ValueError, RecursionError):
            errors += 1
    status = f"Построено графиков: {plotted}"
    if errors:
        status += f"; ошибок: {errors}"
    app.graph_status.set(status)


__all__ = ["GRAPH_COLORS", "GRAPH_FUNCTION_BUTTONS", "GRAPH_NUMBER_BUTTONS", "draw_graph"]
