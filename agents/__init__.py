"""This package provides a factory for creating Wyzvrdz.

Wyzvrdz created from a factory can be used directly as an agent or integrated
with tools and web interfaces.
"""

from __future__ import annotations

from . import agent
from .wyzvrd_factory import WyzvrdFactory

__all__ = ["agent", "WyzvrdFactory"]
