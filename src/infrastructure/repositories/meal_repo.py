# src/infrastructure/repositories/meal_repo.py  (path example)
from src.domain import Meal, MealEntry, Ingredient, IngredientSource
from src.data.database_models import MealModel, MealEntryModel, IngredientModel
from sqlalchemy import func
from datetime import timezone, tzinfo


class MealRepo:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id: int) -> Meal:
        ent: MealModel | None = self.session.get(MealModel, id)
        if ent is None:
            return None  # or raise a NotFound if you define one
        return self._to_domain(ent)

    def find_by_name(self, query: str, limit: int) -> list[Meal]:
        ents: list[MealModel] = (
            self.session.query(MealModel)
            .filter(func.lower(MealModel.name).like(f"%{query.lower()}%"))
            .limit(limit)
            .all()
        )
        return [self._to_domain(e) for e in ents]

    def create(self, domain_meal: Meal) -> Meal:
        ent = MealModel(
            name=domain_meal.name,
            eaten_at=domain_meal.eaten_at.astimezone(timezone.utc),
        )
        self.session.add(ent)
        self.session.flush()  # assign ent.id

        # domain entries: MealEntry(ingredient: Ingredient, quantity_g: float)
        for de in domain_meal.entries:
            ing_id = de.ingredient.id
            if ing_id is None:
                raise ValueError("MealEntry.ingredient.id must be set")
            me = MealEntryModel(
                meal_id=ent.id,
                ingredient_id=ing_id,
                grams=de.quantity_g,
            )
            self.session.add(me)

        self.session.commit()
        return self._to_domain(ent)

    def update(self, meal_id: int, domain_meal: Meal) -> Meal:
        ent = self.session.get(MealModel, meal_id)
        if ent is None:
            return None  # or raise NotFound

        # scalars
        ent.name = domain_meal.name
        ent.eaten_at = domain_meal.eaten_at.astimezone(timezone.utc)

        # replace entries wholesale
        ent.entries.clear()              # relationship name is `entries` on MealModel
        self.session.flush()
        for de in domain_meal.entries:
            ing_id = de.ingredient.id
            if ing_id is None:
                raise ValueError("MealEntry.ingredient.id must be set")
            me = MealEntryModel(
                meal_id=ent.id,
                ingredient_id=ing_id,
                grams=de.quantity_g,
            )
            self.session.add(me)

        self.session.commit()
        return self._to_domain(ent)

    def delete(self, meal_id: int) -> None:
        ent = self.session.get(MealModel, meal_id)
        if ent is None:
            return  # or raise NotFound
        self.session.delete(ent)
        self.session.commit()

    # ——— Conversion helpers ———

    def _to_domain_ingredient(self, row: IngredientModel) -> Ingredient:
        # DB stores source as str; domain wants IngredientSource enum
        return Ingredient(
            id=row.id,
            name=row.name,
            fats_per_100g=row.fats_per_100g,
            proteins_per_100g=row.proteins_per_100g,
            carbs_per_100g=row.carbs_per_100g,
            kcal_per_100g=row.kcal_per_100g,
            source=IngredientSource(row.source),
            external_id=row.external_id,
        )

    def _ensure_utc(self, dt):
        #asume DB times are UTC, attach tzinfo if missing
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt


    def _to_domain(self, ent: MealModel) -> Meal:
        eaten_at = self._ensure_utc(ent.eaten_at)
        entries = [
            MealEntry(
                ingredient=self._to_domain_ingredient(e.ingredient),  # use relationship
                quantity_g=e.grams,
            )
            for e in ent.entries
        ]
        return Meal(
            id=ent.id,
            name=ent.name,
            eaten_at=eaten_at,
            is_favorite=(ent.favorite is not None),  # MealModel has `favorite` relation, not `is_favorite` field
            entries=entries,
        )
