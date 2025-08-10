from typing import ClassVar
from src.shared.exceptions import AppError

class InfrastructureError(AppError):
    code: ClassVar[str] = "INFRASTRUCTURE_ERROR"

class DatabaseError(InfrastructureError):
    '''
    Generic DB failure. 
    Something went wrong inside of DB layer but it isn't a user correctable. 
    Examples: connection dropped, bad SQL etc. 
    '''
    code: ClassVar[str] = "DATABASE_ERROR"

class DatabaseConflict(DatabaseError):
    '''
    Specific, deterministic data conflict. 
    When a write violates constraints or current DB state, it is raised
    when the requiest must change to succeed.
    Violates UNIQUE/PK/FK/CHECK.
    '''
    code: ClassVar[str] = "DATABASE_CONFLICT"

# when doing wildcard import (from src.infrastructure.errors import *) - import everything nicely
__all__ = ["InfrastructureError", "DatabaseError", "DatabaseConflict"]