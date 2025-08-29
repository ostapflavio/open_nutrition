from src.infrastructure.db import db_dependency
from fastapi import APIRouter
from starlette import status
from typing import Annotated
from src.infrastructure.repositories.ingredient_repo import IngredientRepo
from src.services.services_design import IngredientService

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

def get_service(session: db_dependency):
    repo = IngredientRepo(session)
    return IngredientService(repo)

@router.get("/{ingredient_id}", status_code=status.HTTP_200_OK)
def get_ingredient(session: db_dependency, ingredient_id: int):
    pass