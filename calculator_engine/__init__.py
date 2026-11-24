"""Публичные типы вычислительных режимов."""

from .common import BaseCalculator
from .engineering import EngineeringCalculator
from .graphing import GraphingCalculator
from .standard import StandardCalculator

# Backward-compatible name used by the original application and tests.
Calculator = GraphingCalculator

__all__ = [
    "Calculator",
    "BaseCalculator",
    "StandardCalculator",
    "EngineeringCalculator",
    "GraphingCalculator",
]
