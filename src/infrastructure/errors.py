# src/infrastructure/errors.py
from dataclasses import dataclass
from typing import ClassVar
from src.shared.exceptions import AppError

@dataclass
class InfrastructureError(AppError):
    code: ClassVar[str] = "INFRASTRUCTURE_ERROR"

@dataclass
class DatabaseError(InfrastructureError):
    code: ClassVar[str] = "DATABASE_ERROR"