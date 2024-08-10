from __future__ import annotations
from typing import Any

from dataclasses import dataclass

__all__ = (
    "TokenT",
)

@dataclass
class TokenT():
    type: str
    value: Any
    lineno: int
    index: int
    end: int