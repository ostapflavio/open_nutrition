from __future__ import annotations
from datetime import datetime, date 
from pydantic import BaseModel, Field, confloat, ConfigDict
from typing import Optional, List

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

