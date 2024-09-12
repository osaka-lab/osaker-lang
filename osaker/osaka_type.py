from __future__ import annotations

from enum import Enum

__all__ = (
    "OsakaType",
)

class OsakaType(Enum):
    NYAN = str
    CHIYO = int

    @classmethod
    def from_python_type(cls, py_type: type) -> OsakaType:
        return cls._value2member_map_[py_type]

    @classmethod
    def from_osaka_type_string(cls, osaka_type: str) -> OsakaType:
        return cls._member_map_[osaka_type.upper()]