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
    character_number: int

    @property
    def id(self) -> str:
        return f"{self.line_number}{self.type}{self.character_number}"