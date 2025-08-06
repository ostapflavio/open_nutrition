from src.domain import Meal, MealEntry, MacroTotals

from app.database_models import (
    MealModel as MealEntity,
    MealEntryModel as MealEntryEntity,
    FavoriteMealModel as FavoriteMealEntity
)

class MealRepository:
    """
    A repositoty to work with database, meal table
    """

    def __init__(self, session):
        #Define a global session so that we can operate with database
        self.session = session

    def get_by_id(self, id: int) -> Meal:
        """Find the ingredient by id. """
        entity: MealEntity = self.session.get(MealEntity, id)
        return self._to_domain(entity)


    def find_by_name(self, query: str, limit: int) -> list[Meal]:
        """
        Function that returns a list of Meals matching the given name.
        """
        ents: list[MealEntity] = (
            self.session
            .query(MealEntity)
            .filter(MealEntity.name.like(f"%{query.lower()}%"))
            .limit(limit)
            .all()
        )
        return [self._to_domain(e) for e in ents]

    def create(self, domain_meal: Meal) -> Meal:
        # 1) Persist the Meal itself
        ent = MealEntity(
            name=domain_meal.name,
            eaten_at=domain_meal.eaten_at,
        )
        self.session.add(ent)
        self.session.flush()  # so ent.id is assigned

        # 2) Persist each MealEntry
        for de in domain_meal.entries:
            me = MealEntryEntity(
                meal_id=ent.id,
                ingredient_id=de.ingredient_id,
                grams=de.grams,
            )
            self.session.add(me)

        self.session.commit()
        return self._to_domain(ent)

    def update(self, meal_id: int, domain_meal: Meal) -> Meal:
        ent = self.session.get(MealEntity, meal_id)

        # update scalar fields
        ent.name         = domain_meal.name
        ent.eaten_at     = domain_meal.eaten_at

        # replace entries wholesale (simple approach)
        ent.meal_entries.clear()
        self.session.flush()
        for de in domain_meal.entries:
            me = MealEntryEntity(
                meal_id=ent.id,
                ingredient_id=de.ingredient_id,
                grams=de.grams,
            )
            self.session.add(me)

        self.session.commit()
        return self._to_domain(ent)

    def delete(self, meal_id: int) -> None:
        ent = self.session.get(MealEntity, meal_id)
        self.session.delete(ent)
        self.session.commit()

    # ——— Conversion helpers ———

    def _to_domain(self, ent: MealEntity) -> Meal:
        # build domain entries
        entries = [
            MealEntry(
                id=e.id,
                ingredient_id=e.ingredient_id,
                grams=e.grams,
            )
            for e in ent.meal_entries
        ]
        # you could compute macros here or use MacroTotals if you persist them
        # totals = MacroTotals.from_entries(entries)
        return Meal(
            id=ent.id,
            name=ent.name,
            eaten_at=ent.eaten_at,
            is_favourite=ent.is_favourite,
            entries=entries,
            #macro_totals=totals
        )