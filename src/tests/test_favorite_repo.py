from datetime import datetime, timezone
import pytest

from src.infrastructure.repositories.favorite_repo import FavoriteRepo
from src.infrastructure.repositories.meal_repo import MealRepo
from src.domain.errors import MealNotFound, FavoriteAlreadyExists
from src.domain import Meal, MealEntry, Ingredient, IngredientSource
from src.data.database_models import FavoriteMealModel, MealEntryModel, MealModel


# ---------- Helpers ----------

def to_domain_ingredient(im):
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
        eaten_at = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    if entries is None:
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


# ---------- Tests: get() ----------

def test_get_found_returns_domain_meal(session, seed_ingredients):
    by_name, _ = seed_ingredients
    meal_repo = MealRepo(session)
    fav_repo = FavoriteRepo(session=session, meal_repo=meal_repo)

    apple = to_domain_ingredient(by_name["Apple"])
    saved_meal = meal_repo.create(
        make_meal(
            name="Breakfast",
            eaten_at=datetime(2025, 1, 2, 8, 0, tzinfo=timezone.utc),
            entries=[MealEntry(ingredient=apple, quantity_g=120)],
        )
    )

    fav_row = FavoriteMealModel(meal_id=saved_meal.id, name=saved_meal.name)
    session.add(fav_row)
    session.commit()

    got = fav_repo.get(fav_row.id)
    assert isinstance(got, Meal)
    assert got.id == saved_meal.id
    assert got.name == "Breakfast"
    assert got.eaten_at == datetime(2025, 1, 2, 8, 0, tzinfo=timezone.utc)
    assert len(got.entries) == 1
    assert got.entries[0].ingredient.id == apple.id
    assert got.entries[0].quantity_g == 120


def test_get_missing_raises(session):
    fav_repo = FavoriteRepo(session=session, meal_repo=MealRepo(session))
    with pytest.raises(MealNotFound):
        fav_repo.get(999999)


# ---------- Tests: add() ----------

def test_add_persists_and_returns_domain_meal(session, seed_ingredients):
    by_name, _ = seed_ingredients
    meal_repo = MealRepo(session)
    fav_repo = FavoriteRepo(session=session, meal_repo=meal_repo)

    banana = to_domain_ingredient(by_name["Banana"])
    meal = meal_repo.create(
        make_meal(
            name="Lunch",
            eaten_at=datetime(2025, 1, 3, 12, 0, tzinfo=timezone.utc),
            entries=[MealEntry(ingredient=banana, quantity_g=200)],
        )
    )

    out = fav_repo.add(meal.id)

    # returns domain meal
    assert isinstance(out, Meal)
    assert out.id == meal.id
    assert out.name == "Lunch"

    # persisted favorite row
    row = session.query(FavoriteMealModel).filter_by(meal_id=meal.id).first()
    assert row is not None
    assert row.name == "Lunch"


def test_add_duplicate_raises(session, seed_ingredients):
    by_name, _ = seed_ingredients
    meal_repo = MealRepo(session)
    fav_repo = FavoriteRepo(session=session, meal_repo=meal_repo)

    mango = to_domain_ingredient(by_name["Mango"])
    meal = meal_repo.create(
        make_meal(
            name="Snack",
            eaten_at=datetime(2025, 1, 4, 15, 0, tzinfo=timezone.utc),
            entries=[MealEntry(ingredient=mango, quantity_g=50)],
        )
    )

    # first add OK
    fav_repo.add(meal.id)

    # second add -> duplicate
    with pytest.raises(FavoriteAlreadyExists):
        fav_repo.add(meal.id)

    cnt = session.query(FavoriteMealModel).filter_by(meal_id=meal.id).count()
    assert cnt == 1


def test_add_propagates_meal_not_found(session):
    fav_repo = FavoriteRepo(session=session, meal_repo=MealRepo(session))
    with pytest.raises(MealNotFound):
        fav_repo.add(123456789)  # non-existent meal id


# ---------- Tests: delete() ----------

def test_delete_ok_then_get_raises(session, seed_ingredients):
    by_name, _ = seed_ingredients
    meal_repo = MealRepo(session)
    fav_repo = FavoriteRepo(session=session, meal_repo=meal_repo)

    egg = to_domain_ingredient(by_name["Egg"])
    meal = meal_repo.create(
        make_meal(
            name="To Delete",
            entries=[MealEntry(ingredient=egg, quantity_g=70)],
        )
    )

    fav = FavoriteMealModel(meal_id=meal.id, name=meal.name)
    session.add(fav)
    session.commit()
    fav_id = fav.id

    # ensure exists
    assert session.get(FavoriteMealModel, fav_id) is not None

    fav_repo.delete(fav_id)

    # removed
    assert session.get(FavoriteMealModel, fav_id) is None

    with pytest.raises(MealNotFound):
        fav_repo.get(fav_id)


def test_delete_missing_raises(session):
    fav_repo = FavoriteRepo(session=session, meal_repo=MealRepo(session))
    with pytest.raises(MealNotFound):
        fav_repo.delete(42)


# ---------- Tests: update() ----------

def test_update_rewrites_meal_via_meal_repo_and_returns_updated(session, seed_ingredients):
    by_name, _ = seed_ingredients
    meal_repo = MealRepo(session)
    fav_repo = FavoriteRepo(session=session, meal_repo=meal_repo)

    apple = to_domain_ingredient(by_name["Apple"])
    base = meal_repo.create(
        make_meal(
            name="Original",
            eaten_at=datetime(2025, 1, 5, 9, 0, tzinfo=timezone.utc),
            entries=[MealEntry(ingredient=apple, quantity_g=100)],
        )
    )

    fav = FavoriteMealModel(meal_id=base.id, name=base.name)
    session.add(fav)
    session.commit()

    # Build the new domain meal (e.g., rename + different entries)
    updated_domain = make_meal(
        name="Updated",
        eaten_at=datetime(2025, 1, 5, 13, 0, tzinfo=timezone.utc),
        entries=[MealEntry(ingredient=apple, quantity_g=250)],
    )

    updated = fav_repo.update(fav.id, updated_domain)

    assert isinstance(updated, Meal)
    assert updated.id == base.id
    assert updated.name == "Updated"
    assert updated.eaten_at == datetime(2025, 1, 5, 13, 0, tzinfo=timezone.utc)
    assert len(updated.entries) == 1
    assert updated.entries[0].quantity_g == 250

    # persisted
    mrow = session.get(MealModel, base.id)
    assert mrow.name == "Updated"
    cnt = session.query(MealEntryModel).filter_by(meal_id=base.id).count()
    assert cnt == 1


def test_update_missing_favorite_raises(session, seed_ingredients):
    by_name, _ = seed_ingredients
    meal_repo = MealRepo(session)
    fav_repo = FavoriteRepo(session=session, meal_repo=meal_repo)

    apple = to_domain_ingredient(by_name["Apple"])
    domain_meal = make_meal(
        name="Whatever",
        eaten_at=datetime(2025, 1, 6, 10, 0, tzinfo=timezone.utc),
        entries=[MealEntry(ingredient=apple, quantity_g=111)],
    )

    with pytest.raises(MealNotFound):
        fav_repo.update(999999, domain_meal)
