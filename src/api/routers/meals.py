from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from starlette import status

from src.infrastructure.db import db_dependency
from src.services.meals import MealService
from src.services.errors import ValidationError
from src.domain.errors import MealNotFound
from src.domain import Meal

from src.api.schemas import (
    MealCreate,
    MealRead,
    MealUpdate,
    MealEntryRead
)

router = APIRouter(prefix='/meals', tags=['meals'])

# --------- Helpers (Domain -> API) ---------
def _to_meal_read(meal: Meal) -> MealRead:
    entries: list[MealEntryRead] = [
        MealEntryRead(
            id=getattr(e, "id", None),
            ingredient_id=e.ingredient.id,
            grams=e.quantity_g,
        )
        for e in meal.entries
    ]

    return MealRead(
        id=meal.id,
        name=meal.name,
        eaten_at=meal.eaten_at,
        entries=entries,
    )

def _handle_service_exc(exc: Exception):
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Received bad data.")
    if isinstance(exc, MealNotFound):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find meal")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# --------- Endpoints ---------
@router.post("", response_model = MealRead, status_code=status.HTTP_201_CREATED)
def create_meal(payload: MealCreate, db: db_dependency):
    svc = MealService(db)
    try:
        meal = svc.create(
            name=payload.name,
            eaten_at=payload.eaten_at,
            entries=[e.model_dump() for e in payload.entries], # {'ingredient_id': int, 'grams': float}
        )
        return _to_meal_read(meal)
    except Exception as exc:
        _handle_service_exc(exc)

@router.get("/search", response_model=list[MealRead])
def search_meals(
        db: db_dependency,
        q: str = Query(..., min_length=1, description = "Substring of the meal name"),
        limit: int = Query(10, ge=1, le=100),
):
    svc = MealService(db)
    try:
        meals = svc.search(q, limit)
        return [_to_meal_read(m) for m in meals]
    except Exception as exc:
        _handle_service_exc(exc)

@router.get("/{meal_id}", response_model=MealRead)
def get_meal(meal_id: int, db: db_dependency):
    svc = MealService(db)
    try:
        meal = svc.get(meal_id)
        return _to_meal_read(meal)
    except Exception as exc:
        _handle_service_exc(exc)


@router.put("/{meal_id}", response_model=MealRead)
def update_meal(meal_id: int, payload: MealUpdate, db: db_dependency):
    svc = MealService(db)
    try:
        meal = svc.get(meal_id)
        entries_payload = []
        if payload.entries is None:
            entries_payload = [
                {"ingredient_id": e.ingredient.id, "grams": e.quantity_g}
                for e in meal.entries
            ]
        else:
            entries_payload = [e.model_dump() for e in payload.entries]

        updated = svc.update(
            meal_id = meal_id,
            name = payload.name or meal.name,
            eaten_at = payload.eaten_at or meal.eaten_at,
            entries = entries_payload,
        )

        return _to_meal_read(updated)
    except Exception as exc:
        _handle_service_exc(exc)

@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: int, db: db_dependency):
    svc = MealService(db)
    try:
        svc.delete(meal_id)
        return # 204 no content
    except Exception as exc:
        _handle_service_exc(exc)