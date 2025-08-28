from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from types import SimpleNamespace

from sqlalchemy.orm import Session

from src.infrastructure.repositories.meal_repo import MealRepo
# Optional: only if you want to validate ingredient ids exist
# from src.infrastructure.repositories.ingredient_repo import IngredientRepo
from src.domain import Meal, MealEntry 
from src.domain.errors import MealNotFound
from src.services.errors import ValidationError


def _ensure_utc(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.now(tz=timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class MealService:
    """
    Application layer for meal use-cases.
    Keeps transaction/commit in repos (your chosen rule),
    but centralizes domain/application logic & validation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.meals = MealRepo(db)
        # self.ingredients = IngredientRepo(db)  # uncomment if you want validation

    # ---------- Commands / Queries ----------

    # asterisk means that all arguments after that must be passed as keywords 
    # allows cleaner API and prevents bugs from wrong positional ordering
    def create(self, *, name: str, eaten_at: Optional[datetime], entries: List[dict]) -> Meal:
        """
        entries: List[{'ingredient_id': int, 'grams': float}]
        """
        if not name or not name.strip():
            raise ValidationError("Meal name is required.")
        # Optional validation: ensure ingredient IDs exist
        # for e in entries:
        #     self.ingredients.get_by_id(e['ingredient_id'])  # raise if missing

        dom_entries: List[MealEntry] = []
        for e in entries:
            if e["ingredient_id"] is None or e["ingredient_id"] < 1:
                raise ValidationError("ingredient_id must be a positive integer.")
            if e["grams"] < 0:
                raise ValidationError("grams must be >= 0.")
            # We only need ingredient.id for persistence; keep it lightweight:
            ingredient_ref = SimpleNamespace(id=e["ingredient_id"])
            dom_entries.append(MealEntry(ingredient=ingredient_ref, quantity_g=e["grams"]))

        dom_meal = Meal(
            id=None,
            name=name.strip(),
            eaten_at=_ensure_utc(eaten_at),
            is_favorite=False,
            entries=dom_entries,
        )
        return self.meals.create(dom_meal)

    def get(self, meal_id: int) -> Meal:
        return self.meals.get_by_id(meal_id)

    def search(self, q: str, limit: int = 10) -> List[Meal]:
        return self.meals.find_by_name(q, limit)

    def replace(self, meal_id: int, *, name: str, eaten_at: Optional[datetime], entries: List[dict]) -> Meal:
        # Ensure present for clean 404 semantics
        self.get(meal_id)

        # Reuse same rules as create()
        return self.create(name=name, eaten_at=eaten_at, entries=entries) \
            if meal_id is None else self._update_wholesale(meal_id, name, eaten_at, entries)

    def patch_scalars(self, meal_id: int, *, name: Optional[str], eaten_at: Optional[datetime]) -> Meal:
        current = self.get(meal_id)

        new_name = current.name if name is None else name.strip()
        if not new_name:
            raise ValidationError("Meal name cannot be empty.")
        new_eaten = _ensure_utc(current.eaten_at if eaten_at is None else eaten_at)

        # Preserve entries wholesale, just swap scalars
        patched = Meal(
            id=current.id,
            name=new_name,
            eaten_at=new_eaten,
            is_favorite=current.is_favorite,
            entries=current.entries,
        )
        updated = self.meals.update(meal_id, patched)
        if updated is None:
            raise MealNotFound("Meal not found.")
        return updated

    def delete(self, meal_id: int) -> None:
        # Optional: force 404 for not found
        self.get(meal_id)  # raises if missing
        self.meals.delete(meal_id)

    # ---------- Internals ----------

    def _update_wholesale(self, meal_id: int, name: str, eaten_at: Optional[datetime], entries: List[dict]) -> Meal:
        if not name or not name.strip():
            raise ValidationError("Meal name is required.")
        # Optional: validate ingredients as in create()
        dom_entries: List[MealEntry] = []
        for e in entries:
            if e["ingredient_id"] is None or e["ingredient_id"] < 1:
                raise ValidationError("ingredient_id must be a positive integer.")
            if e["grams"] < 0:
                raise ValidationError("grams must be >= 0.")
            ingredient_ref = SimpleNamespace(id=e["ingredient_id"])
            dom_entries.append(MealEntry(ingredient=ingredient_ref, quantity_g=e["grams"]))

        dom_meal = Meal(
            id=meal_id,
            name=name.strip(),
            eaten_at=_ensure_utc(eaten_at),
            is_favorite=False,  # repo can infer from relation if needed
            entries=dom_entries,
        )
        updated = self.meals.update(meal_id, dom_meal)
        if updated is None:
            raise MealNotFound("Meal not found.")
        return updated
