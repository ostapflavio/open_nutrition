from src.shared.exceptions import AppError
from dataclasses import dataclass 
from typing import ClassVar

@dataclass(eq=False)
class ValidationError(AppError):
    """Raise when application receive bad input."""
    code: ClassVar[str] = "VALIDATION_ERROR"
