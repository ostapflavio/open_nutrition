# src/external/errors.py
from dataclasses import dataclass
from typing import ClassVar
from src.shared.exceptions import AppError

@dataclass
class ExternalServiceError(AppError):
    code: ClassVar[str] = "EXTERNAL_SERVICE_ERROR"

@dataclass
class ExternalServiceTimeout(ExternalServiceError):
    code: ClassVar[str] = "EXTERNAL_SERVICE_TIMEOUT"
