from enum import Enum
from typing import List

from pydantic import BaseModel


class InversionType(Enum):
    normal_gold = "gold"
    normal_elixir = "elixir"
    walls = "walls"
    dark_elixir = "dark-elixir"
    constructor_gold = "c-gold"
    constructor_elixir = "c-elixir"

    def __repr__(self) -> str:
        return f"<{self.value}>"


class Inversion(BaseModel):
    concept: str
    inversion_type: InversionType


class InversionManager(BaseModel):
    inversions: List[Inversion]
