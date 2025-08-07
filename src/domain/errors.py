from dataclasses import dataclass
from typing import ClassVar
from src.shared.exceptions import AppError

@dataclass 
class DomainError(AppError):
    code: ClassVar[str] = "DOMAIN_ERROR"

@dataclass 
class InvalidIngredient(DomainError):
    code: ClassVar[str] = "INVALID_INGREDIENT"

@dataclass 
class IngredientNotFound(DomainError):
    code: ClassVar[str] = "INGREDIENT_NOT_FOUND"
    def __init__(self, message: str | None = None, identifier: int | str | None = None):
        if message is None:
            message = f"Ingredient not found{f': {identifier!r}' if identifier is not None else ''}."
        self.identifier = identifier
        self.message = message  
        super().__init__(message)

@dataclass 
class IngredientAlreadyExists(DomainError):
    code: ClassVar[str] = "INGREDIENT_ALREADY_EXISTS"

@dataclass 
class MealNotFound(DomainError):
    code: ClassVar[str] = "MEAL_NOT_FOUND"
    def __init__(self, message: str | None = None, identifier: int | str | None = None):
        if message is None:
            message = f"Meal not found{f': {identifier!r}' if identifier is not None else ''}."
        self.identifier = identifier
        self.message = message  
        super().__init__(message)

@dataclass
class InvalidMeal(DomainError):
    code: ClassVar[str] = "INVALID_MEAL"

@dataclass 
class EmptyMeal(DomainError):
    code: ClassVar[str] = "EMPTY_MEAL"

@dataclass 
class FavoriteAlreadyExists(DomainError):
    code: ClassVar[str] = "FAVORITE_ALREADY_EXISTS"

@dataclass
class ExternalIngredientFormatError(DomainError):
    code: ClassVar[str] = "EXTERNAL_INGREDIENT_FORMAT_ERROR"

@dataclass
class InvalidDateRange(DomainError):
    code: ClassVar[str]  = "INVALID_DATA_RANGE"
