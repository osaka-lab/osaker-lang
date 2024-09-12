from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from .osaka_type import OsakaType

from dataclasses import dataclass

__all__ = (
    "AyumuObject",
)

@dataclass
class AyumuObject():
    type: OsakaType
    value: Any