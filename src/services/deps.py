from typing import Annotated
from fastapi import Depends 

from src.infrastructure.db import db_dependency
from src.services.meals import MealService

def get_meal_service(db: db_dependency) -> MealService:
    return MealService(db)

meal_service_dependency = Annotated[MealService, Depends(get_meal_service)]