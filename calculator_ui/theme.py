"""Общие цвета и оформление интерфейса."""

import sys

IS_MAC = sys.platform == "darwin"

BACKGROUND = "#202020"
BUTTON = "#323232" if not IS_MAC else "#424242"
BUTTON_HOVER = "#3d3d3d" if not IS_MAC else "#505050"
BUTTON_FUNCTION = "#292929" if not IS_MAC else "#353535"
ACCENT = "#4cc2ff" if not IS_MAC else "#2196F3"
TEXT = "#f4f4f4"
MUTED = "#a9a9a9"

__all__ = [
    "IS_MAC",
    "BACKGROUND", "BUTTON", "BUTTON_HOVER", "BUTTON_FUNCTION",
    "ACCENT", "TEXT", "MUTED",
]
