from __future__ import annotations

from dataclasses import dataclass

__all__ = (
    "Token",
)

@dataclass
class Token():
    type: str
    value: str
    line_number: int
    index_number: int