from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from src.infrastructure.repositories.meal_repo import MealRepo
from src.infrastructure.repositories.ingredient_repo import IngredientRepo
from src.domain import Meal, MealEntry, Ingredient
from src.domain.errors import MealNotFound, IngredientNotFound
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
    Keeps transaction/commit in repos
    but centralizes domain/application logic & validation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.meals = MealRepo(db)
        self.ingredients = IngredientRepo(db)

    # ---------- Commands / Queries ----------

    def update_entry_quantity(self, *, meal_id: int, entry_id: int, grams: float) -> None:
        if grams <= 0:
            raise ValidationError("grams must be positive")
        self.meals.get_by_id(meal_id) # check for 404 error
        self.meals.update_entry_quantity(meal_id=meal_id, entry_id=entry_id, grams=grams)

    def update_entry_ingredient(self, *, meal_id: int, entry_id: int, ingredient_id: int) -> None:
        if ingredient_id < 1:
            raise ValidationError("ingredient must greater than one")
        self.meals.get_by_id(meal_id)  # check for 404 error
        try:
            self.ingredients.get_by_id(ingredient_id) # will raise if missing
        except IngredientNotFound:
            raise ValidationError("ingredient_id not found")

        self.meals.update_entry_ingredient(meal_id=meal_id, entry_id=entry_id, ingredient_id=ingredient_id)

    def remove_entry(self, *, meal_id: int, entry_id: int) -> None:
        self.meals.get_by_id(meal_id)  # check for 404 error
        self.meals.delete_entry(meal_id=meal_id, entry_id=entry_id)

    # asterisk means that all arguments after that must be passed as keywords 
    # allows cleaner API and prevents bugs from wrong positional ordering
    def create(self, *, name: str, eaten_at: Optional[datetime], entries: List[dict]) -> Meal:
        """
        entries: List[{'ingredient_id': int, 'grams': float}]
        """
        # TODO: Avoid DRY deviation inside of create() and _update_wholesale()
        if not name or not name.strip():
            raise ValidationError("Meal name is required.")


        dom_entries = self._hydrate_entries(entries)


        dom_meal = Meal(
            id=None,
            name=name.strip(),
            eaten_at=_ensure_utc(eaten_at),
            is_favorite=False, # new meal - don't star it yet
            entries=dom_entries,
        )
        return self.meals.create(dom_meal)

    def get(self, meal_id: int) -> Meal:
        return self.meals.get_by_id(meal_id)

    def list_entries(self, meal_id: int) -> list[MealEntry]:
        meal = self.meals.get_by_id(meal_id)
        return meal.entries

    def search(self, q: str, limit: int = 10) -> List[Meal]:
        return self.meals.find_by_name(q, limit)

    # for PUT 
    def update(self, meal_id: int, *, name: str, eaten_at: Optional[datetime], entries: List[dict]) -> Meal:
        if not name or not name.strip():
            raise ValidationError(message="Meal name is required.", entity="Meal", entity_id=str(meal_id))

        current = self.meals.get_by_id(meal_id)
        dom_entries = self._hydrate_entries(entries)

        dom_meal = Meal(
            id = meal_id,
            name = name.strip(),
            eaten_at = _ensure_utc(eaten_at), 
            is_favorite = current.is_favorite, 
            entries = dom_entries,
        )

        updated = self.meals.update(meal_id, dom_meal)
        if updated is None:
            raise MealNotFound(message="Meal not found.")
        
        return updated 

   
    def delete(self, meal_id: int) -> None:
        # Optional: force 404 for not found
        self.get(meal_id)  # raises if missing
        self.meals.delete(meal_id)

    # ---------- Internals ----------
    def _hydrate_entries(self, entries: List[dict], *, require_non_empty: bool = True) -> List[MealEntry]:
        if entries is None:
            raise ValidationError(message="entries is required for PUT", entity="Meal")

        if require_non_empty and len(entries) == 0:
            raise ValidationError(message="entries cannot be empty for PUT", entity="Meal")

        # Validate shapes and collect ids in original order
        ids_in_order: List[int] = []
        grams_in_order: List[float] = []

        for e in entries:
            iid = e.get("ingredient_id")
            g = e.get("grams")
            if iid is None or iid < 1:
                raise ValidationError(message="ingredient_id must be >= 1", entity="MealEntry")
            if g is None or g <= 0:
                raise ValidationError(message="grams must be > 0", entity="MealEntry")
            ids_in_order.append(iid)
            grams_in_order.append(g)

        # Bulk fetch unique ingredients
        unique_ids = set(ids_in_order)
        ing_map: dict[int, Ingredient] = self.ingredients.get_many(list(unique_ids))

        # Ensure all requested ids exist
        missing_ids = [iid for iid in unique_ids if iid not in ing_map] 
        if missing_ids:
            # Surface bad input as 400
            raise ValidationError(
                message="Couldn't fetch all ingredients! Maybe some of them doesn't even exist...")

        # Build MealEntry in original order (preserve duplicates & order)
        dom_entries: List[MealEntry] = []
        for iid, g in zip(ids_in_order, grams_in_order):
            dom_entries.append(MealEntry(ingredient=ing_map[iid], quantity_g=g))

        return dom_entries