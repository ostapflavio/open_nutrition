from typing import ClassVar
from src.shared.exceptions import AppError

# NOTE: we don't use here @dataclass, because leaf exceptions don't generate any new __init__ and they override baseclass ones 
# ==== Generalized domain errors ====
class DomainError(AppError):
    code: ClassVar[str] = "DOMAIN_ERROR"

class Conflict(DomainError):
    code: ClassVar[str] = "DOMAIN_CONFLICT"

class NotFound(DomainError):
    code: ClassVar[str] = "DOMAIN_NOT_FOUND"
    entity_name: ClassVar[str | None] = None 
    def __init__(self, message: str | None = None, identifier: int | str | None = None):
        ent = self.entity_name or self.__class__.__name__.removesuffix("NotFound")
        if message is None:
            message = f"{ent} not found{f': {identifier!r}' if identifier is not None else ''}."
        super().__init__(
            message = message, 
            entity = ent, 
            entity_id = str(identifier) if identifier is not None else None
        )

class AlreadyExists(Conflict):
    code: ClassVar[str] = "DOMAIN_ALREADY_EXISTS"
    entity_name: ClassVar[str | None] = None
    def __init__(self, message: str | None = None, identifier: int | str | None = None):
        ent = self.entity_name or self.__class__.__name__.removesuffix("AlreadyExists")
        if message is None:
            message = f"{ent} already exists{f': {identifier!r}' if identifier is not None else ''}."
        super().__init__(
            message = message,
            entity = ent,
            entity_id = str(identifier) if identifier is not None else None
        )

# ===== Specific domain errors ====
class InvalidIngredient(DomainError):
    code: ClassVar[str] = "INVALID_INGREDIENT"

class IngredientNotFound(NotFound):
    code: ClassVar[str] = "INGREDIENT_NOT_FOUND"
    entity_name: ClassVar[str] = "Ingredient"

class IngredientAlreadyExists(AlreadyExists):
    code: ClassVar[str] = "INGREDIENT_ALREADY_EXISTS"
    entity_name: ClassVar[str] = "Ingredient"

class MealNotFound(NotFound):
    code: ClassVar[str] = "MEAL_NOT_FOUND"
    entity_name: ClassVar[str] = "Meal"

class InvalidMeal(DomainError):
    code: ClassVar[str] = "INVALID_MEAL"

class EmptyMeal(DomainError):
    code: ClassVar[str] = "EMPTY_MEAL"

class FavoriteAlreadyExists(AlreadyExists):
    code: ClassVar[str] = "FAVORITE_ALREADY_EXISTS"
    entity_name: ClassVar[str] = "Favorite"

class ExternalIngredientFormatError(DomainError):
    code: ClassVar[str] = "EXTERNAL_INGREDIENT_FORMAT_ERROR"

class InvalidDateRange(DomainError):
    code: ClassVar[str]  = "INVALID_DATE_RANGE"