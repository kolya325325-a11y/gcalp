"""Стандартный числовой калькулятор."""

from .common import BaseCalculator


class StandardCalculator(BaseCalculator):
    """Калькулятор с базовыми арифметическими операциями."""


Calculator = StandardCalculator

__all__ = ["Calculator", "StandardCalculator"]
