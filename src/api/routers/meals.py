from src.infrastructure.db import db_dependency
from fastapi import APIRouter
from starlette import status 
from typing import Annotated
from src.infrastructure.repositories.meal_repo import MealRepo
from src.services.meals import MealService #?
router = APIRouter(prefix='/meals', tags=['meals'])

def get_service(session: db_dependency):
    repo = MealRepo(session)
    return MealService(repo)

@router.get('/{meal_id}', status_code=status.HTTP_200_OK)
def get_by_id(meal_id: int):
    pass
