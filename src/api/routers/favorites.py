# src/api/routers/favorites.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from starlette import status

from src.infrastructure.db import db_dependency
from src.services.favorites import FavoriteService
from src.services.errors import ValidationError
from src.api.schemas import FavoriteCreate, FavoriteRead
from src.data.database_models import FavoriteMealModel

router = APIRouter(prefix="/favorites", tags=["favorites"])


# ---------- Helpers ----------
def _to_read(row: FavoriteMealModel) -> FavoriteRead:
    return FavoriteRead(
        id=row.id,
        meal_id=row.meal_id,
        name=row.name,
        starred_at=row.starred_at,
    )

def _handle(exc: Exception):
    if isinstance(exc, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
    )


# ---------- Endpoints ----------
@router.post("", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
def add_favorite(payload: FavoriteCreate, db: db_dependency):
    """
    Star a meal. Returns the created favorite row.
    NOTE: 'name' in FavoriteCreate is currently ignored; favorite name = meal.name.
    """
    svc = FavoriteService(db)
    try:
        # repo/service contract: add() returns the Meal domain object
        svc.add(meal_id=payload.meal_id)

        # We don't have a 'get favorite row by id/meal' method in repo,
        # so we read recent favorites and pick the one for this meal_id.
        rows = svc.list_all(limit=200)
        match = next((r for r in rows if r.meal_id == payload.meal_id), None)
        if match is None:
            # Should not happen unless a race/transaction issue
            raise HTTPException(status_code=500, detail="Favorite created but not found")
        return _to_read(match)
    except Exception as exc:
        _handle(exc)


@router.get("", response_model=list[FavoriteRead])
def list_favorites(db: db_dependency, limit: int = Query(100, ge=1, le=500)):
    svc = FavoriteService(db)
    try:
        rows = svc.list_all(limit=limit)
        return [_to_read(r) for r in rows]
    except Exception as exc:
        _handle(exc)


@router.get("/search", response_model=list[FavoriteRead])
def search_favorites(
    db: db_dependency,
    q: str = Query(..., min_length=1, description="Substring of the favorite name (mirrors meal name)"),
    limit: int = Query(50, ge=1, le=500),
):
    svc = FavoriteService(db)
    try:
        rows = svc.search(q=q, limit=limit)
        return [_to_read(r) for r in rows]
    except Exception as exc:
        _handle(exc)


@router.get("/{favorite_id}", response_model=FavoriteRead)
def get_favorite(favorite_id: int, db: db_dependency):
    """
    Return a favorite row by id.
    (Repo lacks a 'get row' method; we search in a recent window.)
    """
    svc = FavoriteService(db)
    try:
        rows = svc.list_all(limit=500)
        match = next((r for r in rows if r.id == favorite_id), None)
        if match is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
        return _to_read(match)
    except Exception as exc:
        _handle(exc)


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(favorite_id: int, db: db_dependency):
    svc = FavoriteService(db)
    try:
        svc.delete(favorite_id)
        return  # 204 No Content
    except Exception as exc:
        _handle(exc)
