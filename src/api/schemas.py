from __future__ import annotations
from datetime import datetime, date 
from pydantic import BaseModel, Field, confloat, ConfigDict
from typing import Optional, List, Literal, Dict


# --------------------
# Utility
# --------------------

class DateRange(BaseModel):
    start: date = Field(...)
    end: date   = Field(...) 

# --------------------
# Ingredients
# --------------------

class IngredientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=512)
    kcal_per_100g: float = Field(..., ge=0)
    carbs_per_100g: float = Field(..., ge=0)
    fats_per_100g: float = Field(..., ge=0)
    proteins_per_100g: float = Field(..., ge=0)


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=512)
    kcal_per_100g: Optional[float] = Field(default=None, ge=0)
    carbs_per_100g: Optional[float] = Field(default=None, ge=0)
    fats_per_100g: Optional[float] = Field(default=None, ge=0)
    proteins_per_100g: Optional[float] = Field(default=None, ge=0)

# elipsis mean that the Field is a required attribute from the user
class IngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(...)
    name: str = Field(...)
    kcal_per_100g: float = Field(...)
    carbs_per_100g: float = Field(...)
    fats_per_100g: float = Field(...)
    proteins_per_100g: float = Field(...)

# --------------------
# Meals
# --------------------

class MealEntryCreate(BaseModel):
    ingredient_id: int = Field(..., ge=1)
    grams: float = Field(..., ge=0) 

class MealEntryUpdate(BaseModel):
    grams: Optional[float] = Field(default = None, ge=0)
    ingredient_id: Optional[int] = Field(default = None, ge = 1)
class MealEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None)
    ingredient_id: int = Field(...)
    grams: float = Field(...)

class MealCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=512)
    eaten_at: Optional[datetime] = Field(default=None)
    entries: List[MealEntryCreate] = Field(default_factory=list)

class MealUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=512)
    eaten_at: Optional[datetime] = Field(default=None)
    entries: Optional[List[MealEntryCreate]] = Field(default=None)

class MealRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(...)
    name: str = Field(...)
    eaten_at: datetime = Field(...)
    entries: List[MealEntryRead] = Field(default_factory=list)

# ----------------------------
# FAVORITES
# ----------------------------

class FavoriteCreate(BaseModel):
    meal_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=512)


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(...)
    meal_id: int = Field(...)
    name: str = Field(...)
    starred_at: datetime = Field(...)


# ----------------------------
# STATS
# ----------------------------

class DayCaloriesRead(BaseModel):
    day: date = Field(..., description = "Calendar day (YYYY-MM-DD")
    calories: float = Field(..., description="Total kcal for this day")

class MacroPercentagesRead(BaseModel):
    protein_pct: float = Field(..., description="Protein percentage (0..100")
    carbs_pct: float = Field(..., description="Carbs percentage (0..100)")
    fat_pct: float = Field(..., description="Fat percentage (0..100)")

class StatsRead(BaseModel):
    days: list[DayCaloriesRead] = Field(..., description="Zero-filled daily kcal series")
    macro_pct: MacroPercentagesRead = Field(..., description="Macro split over the whole range")
    basis: Literal["kcal", "grams"] = Field("kcal", description="What the macro percetanges are based on: 'kcal' or 'grams'")

# ----------------------------
# History
# ----------------------------

class HistoryMealRead(BaseModel):
    id: int
    name: str
    eaten_at: datetime
    kcal: Optional[float] = None
    # Optional HATEOAS-like action URLs for your UI to call:
    actions: Dict[str, str] = Field(
        default_factory=dict,
        description="Links to update/delete/star for this meal."
    )

class HistoryDayRead(BaseModel):
    day: date  # Local day in the provided timezone
    total_kcal: Optional[float] = None
    meals: List[HistoryMealRead]

class HistorySummaryRead(BaseModel):
    day_count: int
    meal_count: int
    total_kcal: Optional[float] = None

class HistoryRead(BaseModel):
    range_start: datetime
    range_end: datetime
    timezone: str                      # IANA timezone name for correct time conversion
    days: List[HistoryDayRead]
    summary: HistorySummaryRead