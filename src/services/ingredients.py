from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session

from src.infrastructure.repositories.ingredient_repo import IngredientRepo
from src.domain import Ingredient
from src.domain.errors import IngredientNotFound  # make sure this exists; mirror MealNotFound
from src.services.errors import ValidationError


def _ensure_non_negative(value: Optional[float], field: str) -> float:
    if value is None:
        raise ValidationError(message=f"{field} is required.", entity="Ingredient")
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValidationError(message=f"{field} must be a number.", entity="Ingredient")
    if v < 0:
        raise ValidationError(message=f"{field} must be >= 0.", entity="Ingredient")
    return v


class IngredientService:
    """
    Application layer for ingredient use-cases.
    Keeps transaction/commit in repos
    but centralizes domain/application logic & validation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.ingredients = IngredientRepo(db)

    # ---------- Commands / Queries ----------

    # Use keyword-only args to prevent positional mistakes like in MealService
    def create(
        self,
        *,
        name: str,
        kcal_per_100g: float,
        carbs_per_100g: float,
        fats_per_100g: float,
        proteins_per_100g: float,
    ) -> Ingredient:
        if not name or not name.strip():
            raise ValidationError("Ingredient name is required.")

        kcal = _ensure_non_negative(kcal_per_100g, "kcal_per_100g")
        carbs = _ensure_non_negative(carbs_per_100g, "carbs_per_100g")
        fats = _ensure_non_negative(fats_per_100g, "fats_per_100g")
        proteins = _ensure_non_negative(proteins_per_100g, "proteins_per_100g")

        dom_ing = Ingredient(
            id=None,
            name=name.strip(),
            kcal_per_100g=kcal,
            carbs_per_100g=carbs,
            fats_per_100g=fats,
            proteins_per_100g=proteins,
        )
        return self.ingredients.create(dom_ing)

    def get(self, ingredient_id: int) -> Ingredient:
        return self.ingredients.get_by_id(ingredient_id)

    def search(self, q: str, limit: int = 10) -> List[Ingredient]:
        return self.ingredients.find_by_name(q, limit)

    def update(
        self,
        ingredient_id: int,
        *,
        name: str,
        kcal_per_100g: float,
        carbs_per_100g: float,
        fats_per_100g: float,
        proteins_per_100g: float,
    ) -> Ingredient:
        if not name or not name.strip():
            raise ValidationError(
                message="Ingredient name is required.",
                entity="Ingredient",
                entity_id=str(ingredient_id),
            )

        # Ensure it exists; also lets us preserve any fields you might add later
        current = self.ingredients.get_by_id(ingredient_id)

        kcal = _ensure_non_negative(kcal_per_100g, "kcal_per_100g")
        carbs = _ensure_non_negative(carbs_per_100g, "carbs_per_100g")
        fats = _ensure_non_negative(fats_per_100g, "fats_per_100g")
        proteins = _ensure_non_negative(proteins_per_100g, "proteins_per_100g")

        updated = self.ingredients.update(
            ingredient_id,
            name=name.strip(),
            kcal_per_100g=kcal,
            carbs_per_100g=carbs,
            fats_per_100g=fats,
            proteins_per_100g=proteins,
        )
        return updated

    def delete(self, ingredient_id: int) -> None:
        # Optional: force 404 for not found like in MealService
        self.get(ingredient_id)  # raises if missing
        self.ingredients.delete(ingredient_id)
