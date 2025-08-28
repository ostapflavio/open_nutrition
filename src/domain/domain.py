from __future__ import annotations 
from dataclasses import dataclass
from datetime import datetime 

# ---------- Entities ----------
@dataclass
class Ingredient: 
    name: str
    fats_per_100g:    float 
    proteins_per_100g: float
    carbs_per_100g:   float 
    kcal_per_100g:    float
    id: int | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ingredient):
            return NotImplemented
        return (self.id is not None and other.id is not None and self.id == other.id)

@dataclass
class Meal:
    name: str
    eaten_at: datetime
    entries: list[MealEntry]
    is_favorite: bool = False 
    id: int | None = None

    def __post_init__(self):
        if self.eaten_at.tzinfo is None:
            raise ValueError("eaten_at must be timezone-aware (UTC)")

    def compute_totals(self) -> MacroTotals:
        pass
    
# ---------- Value Objects ----------
@dataclass
class MealEntry:
    ingredient: Ingredient
    quantity_g: float

    def __post_init__(self):
        if self.quantity_g <= 0:
            raise ValueError("quantity_g must be > 0")

    def compute_macros(self) -> MacroTotals:
        pass

   
@dataclass(frozen = True)
class MacroTotals:
    proteins: float
    fats:     float 
    carbs:    float 
    kcal:     float 

    def __add__(self, other: MacroTotals) -> MacroTotals:
        return MacroTotals(
                proteins = self.proteins + other.proteins, 
                fats     = self.fats     + other.fats, 
                carbs    = self.carbs    + other.carbs,
                kcal     = self.kcal     + other.kcal) 

    @staticmethod 
    def zero() -> MacroTotals:
        return MacroTotals(
                proteins = 0, 
                fats = 0, 
                carbs = 0,
                kcal = 0)
    
    def ratios(self) -> dict[str, float]:
        pass

@dataclass(frozen = True)
class DataRange:
    start: datetime 
    end:   datetime 

    def __post_init__(self):
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("DataRange datetimes mut be timezone-aware")

        if self.end < self.start:
            raise ValueError("DataRange.end must be >= start")
