# src/tests/test_meal.py
from datetime import datetime, timezone, timedelta
import pytest

from src.domain import Meal, MealEntry, Ingredient, IngredientSource
from src.data.database_models import MealModel, MealEntryModel, IngredientModel
from src.infrastructure.repositories.meal_repo import MealRepo  # adjust if needed


# ---------- Helpers ----------

def to_domain_ingredient(im: IngredientModel) -> Ingredient:
    # Convert DB row -> domain Ingredient (enum conversion included)
    return Ingredient(
        id=im.id,
        name=im.name,
        fats_per_100g=im.fats_per_100g,
        proteins_per_100g=im.proteins_per_100g,
        carbs_per_100g=im.carbs_per_100g,
        kcal_per_100g=im.kcal_per_100g,
        source=IngredientSource(im.source),
        external_id=im.external_id,
    )


def make_meal(
    name: str = "Test Meal",
    eaten_at: datetime | None = None,
    entries: list[MealEntry] | None = None,
    is_favorite: bool = False,
) -> Meal:
    if eaten_at is None:
        eaten_at = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)  # tz-aware (domain requires)
    if entries is None:
        # placeholder entry; tests usually override with seeded ingredients
        fake_ing = Ingredient(
            id=1, name="X", fats_per_100g=0, proteins_per_100g=0,
            carbs_per_100g=0, kcal_per_100g=0, source=IngredientSource.CUSTOM,
            external_id="X"
        )
        entries = [MealEntry(ingredient=fake_ing, quantity_g=100)]
    return Meal(
        id=None,
        name=name,
        eaten_at=eaten_at,
        is_favorite=is_favorite,
        entries=entries,
    )


# ---------- Tests ----------

def test_create_persists_parent_and_entries(session, seed_ingredients):
    by_name, _ = seed_ingredients  # mapping of IngredientModel, e.g. by_name["Apple"]
    repo = MealRepo(session)

    apple = to_domain_ingredient(by_name["Apple"])
    banana = to_domain_ingredient(by_name["Banana"])

    dm = make_meal(
        name="Lunch",
        eaten_at=datetime(2025, 1, 1, 13, 0, tzinfo=timezone.utc),
        entries=[
            MealEntry(ingredient=apple, quantity_g=150),
            MealEntry(ingredient=banana, quantity_g=80),
        ],
    )
    created = repo.create(dm)

    # domain checks
    assert isinstance(created, Meal)
    assert created.id is not None
    assert created.name == "Lunch"
    assert len(created.entries) == 2
    ids = {e.ingredient.id for e in created.entries}
    assert ids == {apple.id, banana.id}
    qtys = {e.quantity_g for e in created.entries}
    assert qtys == {150, 80}

    # DB checks
    row = session.get(MealModel, created.id)
    assert row is not None
    cnt = session.query(MealEntryModel).filter_by(meal_id=created.id).count()
    assert cnt == 2


def test_get_by_id_found(session, seed_ingredients):
    by_name, _ = seed_ingredients
    repo = MealRepo(session)

    mango = to_domain_ingredient(by_name["Mango"])
    saved = repo.create(
        make_meal(
            name="Breakfast",
            eaten_at=datetime(2025, 1, 2, 8, 0, tzinfo=timezone.utc),
            entries=[MealEntry(ingredient=mango, quantity_g=120)],
        )
    )

    got = repo.get_by_id(saved.id)
    assert isinstance(got, Meal)
    assert got.id == saved.id
    assert got.name == "Breakfast"
    assert got.eaten_at == datetime(2025, 1, 2, 8, 0, tzinfo=timezone.utc)
    assert len(got.entries) == 1
    assert got.entries[0].ingredient.id == mango.id
    assert got.entries[0].quantity_g == 120


def test_find_by_name_case_insensitive(session, seed_ingredients):
    by_name, _ = seed_ingredients
    repo = MealRepo(session)

    apple = to_domain_ingredient(by_name["Apple"])
    banana = to_domain_ingredient(by_name["Banana"])
    egg = to_domain_ingredient(by_name["Egg"])

    repo.create(make_meal("Chicken Soup",
                          entries=[MealEntry(ingredient=apple, quantity_g=50)]))
    repo.create(make_meal("chicken salad",
                          entries=[MealEntry(ingredient=banana, quantity_g=60)]))
    repo.create(make_meal("Beef Stew",
                          entries=[MealEntry(ingredient=egg, quantity_g=70)]))

    results = repo.find_by_name("CHICK", limit=10)
    names = {r.name.lower() for r in results}
    assert "chicken soup" in names
    assert "chicken salad" in names


def test_find_by_name_limit(session, seed_ingredients):
    by_name, _ = seed_ingredients
    repo = MealRepo(session)

    apple = to_domain_ingredient(by_name["Apple"])
    banana = to_domain_ingredient(by_name["Banana"])
    mango = to_domain_ingredient(by_name["Mango"])

    repo.create(make_meal("Pasta Primavera",
                          entries=[MealEntry(ingredient=apple, quantity_g=80)]))
    repo.create(make_meal("Pasta Carbonara",
                          entries=[MealEntry(ingredient=banana, quantity_g=90)]))
    repo.create(make_meal("Pastitsio",
                          entries=[MealEntry(ingredient=mango, quantity_g=100)]))

    results = repo.find_by_name("pasta", limit=2)
    assert len(results) == 2  # respects limit


def test_find_by_name_no_match(session):
    repo = MealRepo(session)
    results = repo.find_by_name("zzzz", limit=5)
    assert results == []


def test_update_replaces_entries_and_updates_scalars(session, seed_ingredients):
    by_name, _ = seed_ingredients
    repo = MealRepo(session)

    apple = to_domain_ingredient(by_name["Apple"])
    banana = to_domain_ingredient(by_name["Banana"])
    mango = to_domain_ingredient(by_name["Mango"])

    base = repo.create(
        make_meal(
            name="Original",
            eaten_at=datetime(2025, 1, 3, 9, 0, tzinfo=timezone.utc),
            entries=[
                MealEntry(ingredient=apple, quantity_g=100),
                MealEntry(ingredient=banana, quantity_g=50),
            ],
        )
    )

    updated_domain = make_meal(
        name="Updated",
        eaten_at=datetime(2025, 1, 3, 13, 0, tzinfo=timezone.utc),
        entries=[MealEntry(ingredient=mango, quantity_g=200)],
    )
    updated = repo.update(base.id, updated_domain)

    assert updated.id == base.id
    assert updated.name == "Updated"
    assert updated.eaten_at == datetime(2025, 1, 3, 13, 0, tzinfo=timezone.utc)
    assert len(updated.entries) == 1
    assert updated.entries[0].ingredient.id == mango.id
    assert updated.entries[0].quantity_g == 200

    # DB reflects replacement (only one row now)
    cnt = session.query(MealEntryModel).filter_by(meal_id=base.id).count()
    assert cnt == 1
    only = session.query(MealEntryModel).filter_by(meal_id=base.id).first()
    assert only.ingredient_id == mango.id
    assert only.grams == 200


def test_delete_removes_meal_and_child_entries(session, seed_ingredients):
    by_name, _ = seed_ingredients
    repo = MealRepo(session)

    apple = to_domain_ingredient(by_name["Apple"])
    banana = to_domain_ingredient(by_name["Banana"])

    saved = repo.create(
        make_meal(
            name="To Delete",
            entries=[
                MealEntry(ingredient=apple, quantity_g=70),
                MealEntry(ingredient=banana, quantity_g=30),
            ],
        )
    )
    meal_id = saved.id

    # ensure rows exist
    assert session.get(MealModel, meal_id) is not None
    assert session.query(MealEntryModel).filter_by(meal_id=meal_id).count() == 2

    repo.delete(meal_id)

    # parent removed
    assert session.get(MealModel, meal_id) is None
    # children should be gone (relationship cascade 'all, delete-orphan')
    assert session.query(MealEntryModel).filter_by(meal_id=meal_id).count() == 0
