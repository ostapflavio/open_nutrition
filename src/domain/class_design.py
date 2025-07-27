from __future__ import annotations 
from enum import Enum 
from dataclasses import dataclass 
from datetime import datetime 

# Entities
@dataclass
class Ingredient: 
    id: int | None
    name: str
    fats_per_100g:    float 
    proteins_per_100g: float
    carbs_per_100g:   float 
    kcal_per_100g:    float
    source: IngredientSource 
    external_id: str | None

@dataclass
class Meal:
    id: int
    name: str
    timestamp: datetime
    entries: list[MealEntry]
    is_favorite: bool = False 

    def compute_totals(self) -> MacroTotals:
        pass
    
# Value objects
class IngredientSource(Enum): 
    USDA = "usda"  
    CUSTOM = "custom"

@dataclass
class MealEntry:
    ingredient: Ingredient
    quantity_g: float

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

# Handle Errors 
@dataclass 
class AppError(Exception):
    code: str                        # "INGREDIENT_NOT_FOUND" 
    message: str                     # human redable 
    entity: str | None = None        # "Ingredient", "Meal"
    entity_id: str | None = None 

@dataclass
class IngredientNotFound(AppError):
      

@dataclass
class IngredientAlreadyExists(AppError):
    pass

@dataclass
class InvalidIngredient(AppError):
    pass

@dataclass
class MealNotFound(AppError):
    pass

@dataclass
class InvalidMeal(AppError):
    pass 

@dataclass
class FavoriteAlreadyExists(AppError):
    pass

@dataclass
class EmptyMeal(AppError):
    pass

@dataclass
class InvalidDateRange(AppError):
    pass

@dataclass
class ExternalServiceError(AppError):
    pass

@dataclass
class ExternalServiceTimeout(AppError):
    pass

@dataclass
class ExternalIngredientFormatError(AppError):
    pass

@dataclass
class DatabaseError(AppError):
    pass

@dataclass
class UnexpectedError(AppError):
    pass


