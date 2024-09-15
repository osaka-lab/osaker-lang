from __future__ import annotations

from enum import Enum
from devgoldyutils import Colours

__all__ = (
    "OsakaType",
)

class OsakaType(Enum):
    NYAN = str
    CHIYO = int
    TOMO = bool

    @classmethod
    def from_python_type(cls, py_type: type) -> OsakaType:
        return cls._value2member_map_[py_type]

    @classmethod
    def from_osaka_type_string(cls, osaka_type: str) -> OsakaType:
        return cls._member_map_[osaka_type.upper()]

    def get_resp_colour(self) -> Colours:

        type_to_colour_map = {
            "NYAN": Colours.ORANGE,
            "CHIYO": Colours.CLAY,
            "TOMO": Colours.BLUE
        }

        return type_to_colour_map.get(self.name, Colours.RESET)