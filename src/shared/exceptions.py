from dataclasses import dataclass 
from typing import ClassVar

@dataclass(eq=False)
class AppError(Exception):
    code: ClassVar[str] = "APP_ERROR"                       
    message: str                     # human redable 
    entity: str | None = None        # "Ingredient", "Meal"
    entity_id: str | None = None 

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self): return f"{self.code}: {self.message}"