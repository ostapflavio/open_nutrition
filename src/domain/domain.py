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
        """Sum macros across all entries."""
        total = MacroTotals.zero()
        for e in self.entries:
            total = total + e.compute_macros()
        return total

# ---------- Value Objects ----------
@dataclass
class MealEntry:
    ingredient: Ingredient
    quantity_g: float
    id: int | None = None # allow user change an exact ingredient for PATCH operation
    def __post_init__(self):
        if self.quantity_g <= 0:
            raise ValueError("quantity_g must be > 0")

    def compute_macros(self) -> MacroTotals:
        """ Scale ingredient's per_100g macros to this entriy's grams."""
        factor = self.quantity_g / 100
        return MacroTotals(
            kcal=self.ingredient.kcal_per_100g * factor,
            proteins=self.ingredient.proteins_per_100g * factor,
            carbs=self.ingredient.carbs_per_100g * factor,
            fats=self.ingredient.fats_per_100g * factor,
        )

   
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
        """
        Return macro calorie share as fractions of macro-derived kcal.
        Protein=4 , Carbs=4, Fats=9 kcal/g. If total are zero, return 0.
        Note: We normalize by (4P + 4C + 9F) instead of self.kcal to avoid rounding/fiber drift
        """

        protein_kcal = self.proteins * 4.0
        carb_kcal = self.carbs * 4.0
        fat_kcal = self.fats * 4.0

        macro_kcal = protein_kcal + carb_kcal + fat_kcal
        if macro_kcal <= 0:
            return {"proteins": 0, "carbs": 0, "fats": 0}
        return {
            "proteins": protein_kcal / macro_kcal,
            'fat': fat_kcal / macro_kcal,
            'carb': carb_kcal / macro_kcal,
        }

@dataclass(frozen = True)
class DataRange:
    start: datetime 
    end:   datetime 

    def __post_init__(self):
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("DataRange datetimes mut be timezone-aware")

        if self.end < self.start:
            raise ValueError("DataRange.end must be >= start")
