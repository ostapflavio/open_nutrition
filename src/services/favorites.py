# src/services/favorites.py
from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session

from src.infrastructure.repositories.meal_repo import MealRepo
from src.infrastructure.repositories.favorite_repo import FavoriteRepo
from src.services.errors import ValidationError
from src.domain.errors import MealNotFound, FavoriteNotFound, FavoriteAlreadyExists
from src.domain.domain import Meal
from src.data.database_models import FavoriteMealModel


class FavoriteService:
    """
    Thin service layer over FavoriteRepo.
    Keeps input validation and translates domain errors to ValidationError
    so your routers can return consistent HTTP codes.
    """

    def __init__(self, db: Session):
        self._db = db
        self._meals = MealRepo(db)
        self._favs = FavoriteRepo(db, self._meals)

    # -------- Commands --------
    def add(self, *, meal_id: int) -> Meal:
        """Star a meal by its id. Returns the Meal domain object."""
        if meal_id is None or meal_id < 1:
            raise ValidationError("meal_id must be >= 1")
        try:
            return self._favs.add(meal_id)
        except MealNotFound:
            raise ValidationError("Meal not found")
        except FavoriteAlreadyExists:
            raise ValidationError("Meal is already in favorites")

    def delete(self, favorite_id: int) -> None:
        """Unstar by favorite row id."""
        if favorite_id is None or favorite_id < 1:
            raise ValidationError("favorite_id must be >= 1")
        try:
            self._favs.delete(favorite_id)
        except FavoriteNotFound:
            raise ValidationError("Favorite not found")

    def update(self, favorite_id: int, *, meal: Meal) -> Meal:
        """
        Update the underlying Meal via the favorite handle.
        Mirrors FavoriteRepo.update(favorite_id, domain_meal).
        """
        if favorite_id is None or favorite_id < 1:
            raise ValidationError("favorite_id must be >= 1")
        if meal is None:
            raise ValidationError("meal payload is required")
        try:
            return self._favs.update(favorite_id, meal)
        except FavoriteNotFound:
            raise ValidationError("Favorite not found")
        except MealNotFound:
            raise ValidationError("Meal not found")

    # -------- Queries --------
    def get_meal(self, favorite_id: int) -> Meal:
        """Get the Meal domain object for a given favorite id."""
        if favorite_id is None or favorite_id < 1:
            raise ValidationError("favorite_id must be >= 1")
        try:
            return self._favs.get(favorite_id)
        except FavoriteNotFound:
            raise ValidationError("Favorite not found")

    def search(self, q: str, limit: int = 50) -> List[FavoriteMealModel]:
        """Search favorite rows by name. Returns FavoriteMealModel list."""
        if not q or not q.strip():
            raise ValidationError("q is required")
        if limit < 1 or limit > 500:
            raise ValidationError("limit must be between 1 and 500")
        return self._favs.search(q.strip(), limit)

    def list_all(self, limit: int = 100) -> List[FavoriteMealModel]:
        """List recent favorites. Returns FavoriteMealModel list."""
        if limit < 1 or limit > 500:
            raise ValidationError("limit must be between 1 and 500")
        return self._favs.list_all(limit)
