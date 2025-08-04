from dataclasses import dataclass 
from typing import ClassVar

@dataclass 
class AppError(Exception):
    code: ClassVar[str] = "APP_ERROR"                        # "INGREDIENT_NOT_FOUND" 
    message: str                     # human redable 
    entity: str | None = None        # "Ingredient", "Meal"
    entity_id: str | None = None 
    def __str__(self): return f"{self.code}: {self.message}"