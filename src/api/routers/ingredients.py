from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from starlette import status
from starlette.responses import Response

from src.infrastructure.db import db_dependency
from src.services.ingredients import IngredientService
from src.services.errors import ValidationError
from src.domain.errors import IngredientNotFound
from src.domain import Ingredient

from src.api.schemas import (
    IngredientCreate,
    IngredientRead,
    IngredientUpdate,
)

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

# --------------- Helpers (Domain -> API) -----
def _to_ing_read(ing: Ingredient) -> IngredientRead:
    return IngredientRead(
        id = ing.id,
        name = ing.name,
        kcal_per_100g = ing.kcal_per_100g,
        carbs_per_100g = ing.carbs_per_100g,
        fats_per_100g = ing.fats_per_100g,
        proteins_per_100g = ing.proteins_per_100g,
    )

def _handle_service_exc(exc: Exception):
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Recieved bad data.")
    if isinstance(exc, IngredientNotFound):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find ingredient")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ------------ Endpoints --------
@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(payload: IngredientCreate, db: db_dependency):
    svc = IngredientService(db)
    try:
        ing = svc.create(
            name=payload.name,
            kcal_per_100g = payload.kcal_per_100g,
            carbs_per_100g = payload.carbs_per_100g,
            fats_per_100g = payload.fats_per_100g,
            proteins_per_100g = payload.proteins_per_100g,
        )
        return _to_ing_read(ing)
    except Exception as e:
        _handle_service_exc(e)

@router.get("/search", response_model=list[IngredientRead])
def serach_ingredient(db: db_dependency, q: str = Query(..., min_length=1, description = "Substring of the ingredient name"), limit: int = Query(10, ge=1, le=100)):
    svc = IngredientService(db)
    try:
        items = svc.search(q, limit)
        return [_to_ing_read(x) for x in items]
    except Exception as e:
        _handle_service_exc(e)

@router.get("/{ingredient_id}", response_model=IngredientRead)
def get_ingredient(ingredient_id: int, db: db_dependency):
    svc = IngredientService(db)
    try:
        ing = svc.get(ingredient_id)
        return _to_ing_read(ing)
    except Exception as e:
        _handle_service_exc(e)

@router.put("/{ingredient_id}", response_model=IngredientRead)
def update_ingredient(db: db_dependency, ingredient_id: int, payload: IngredientUpdate):
    svc = IngredientService(db)
    try:
        current = svc.get(ingredient_id)
        updated = svc.update(
            ingredient_id=ingredient_id,
            name=payload.name or current.name,
            kcal_per_100g=payload.kcal_per_100g if payload.kcal_per_100g is not None else current.kcal_per_100g,
            carbs_per_100g=payload.carbs_per_100g if payload.carbs_per_100g is not None else current.carbs_per_100g,
            fats_per_100g=payload.fats_per_100g if payload.fats_per_100g is not None else current.fats_per_100g,
            proteins_per_100g=payload.proteins_per_100g if payload.proteins_per_100g is not None else current.proteins_per_100g,
        )
        return _to_ing_read(updated)
    except Exception as exc:
        _handle_service_exc(exc)

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(db: db_dependency, ingredient_id: int):
    svc = IngredientService(db)
    try:
        svc.delete(ingredient_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        _handle_service_exc(e)