import pytest 

from src.infrastructure.repositories.ingredient_repo import IngredientRepo 
from src.domain.errors import IngredientNotFound
from src.domain.domain import Ingredient, IngredientSource 
from src.data.database_models import IngredientModel

def test_get_by_id_found(session, seed_ingredients):
    by_name, _ = seed_ingredients
    target  = by_name['Apple']
    repo = IngredientRepo(session)


    got = repo.get_by_id(target.id)
    print(got)
    assert isinstance(got, Ingredient)
    assert got.id == target.id
    assert got.name == "Apple"
    assert got.source == IngredientSource.CUSTOM

def test_get_by_id_missing_raises(session):
    repo = IngredientRepo(session)
    with pytest.raises(IngredientNotFound):
        repo.get_by_id(999999)

def test_find_by_name_case_insensitive(session, seed_ingredients):
    # should match 'Banana, 'Mango for 'an (case-sensitive)
    repo = IngredientRepo(session)
    results = repo.find_by_name("An")
    names = {r.name for r in results}
    assert "Banana" in names 
    assert "Mango" in names

def test_find_by_name_limit(session, seed_ingredients):
    repo = IngredientRepo(session)
    results = repo.find_by_name("an", limit = 2)
    assert len(results) == 2

def test_find_by_name_no_match(session, seed_ingredients):
    repo = IngredientRepo(session)
    results = repo.find_by_name("zzzz")
    assert results == []

def test_create_persists_and_converts_source(session):
    repo = IngredientRepo(session)
    domain_ingredient = Ingredient(
        name="Greek Yogurt",
        kcal_per_100g=59.0,
        carbs_per_100g=3.6, 
        proteins_per_100g=10.0,
        fats_per_100g=0.4,
        source=IngredientSource.USDA, 
        external_id="APPROVED!"
    )
    created = repo.create(domain_ingredient)

    assert isinstance(created, Ingredient)
    assert created.name == "Greek Yogurt"
    assert created.source == IngredientSource.USDA
    assert created.external_id == "APPROVED!"

    # check type safety
    row = session.get(IngredientModel, created.id)
    assert isinstance(row.source, str)
    assert row.source == IngredientSource.USDA.value 

def test_update_by_id_changes_fields_and_source(session, seed_ingredients):
    by_name, _ = seed_ingredients
    target = by_name["Banana"]
    repo = IngredientRepo(session)

    updated = repo.update(
        target.id, 
        name="Banana (ripe)",
        kcal_per_100g=100.0,
        proteins_per_100g=1.2,
        source=IngredientSource.USDA,
        external_id="BMW123",
    )

    assert updated.id == target.id
    assert updated.name == "Banana (ripe)"
    assert updated.kcal_per_100g == 100.0
    assert updated.proteins_per_100g == 1.2
    assert updated.source == IngredientSource.USDA
    assert updated.external_id == "BMW123"

    # persisted in DB as strings / numbers 
    row = session.get(IngredientModel, target.id)
    assert row.name == "Banana (ripe)"
    assert row.kcal_per_100g == 100.0
    assert row.proteins_per_100g == 1.2
    assert row.source == IngredientSource.USDA.value
    assert row.external_id == "BMW123"

def test_update_by_name_first_match(session, seed_ingredients):
    by_name, _ = seed_ingredients
    repo = IngredientRepo(session)

    updated = repo.update(
        "Apple", 
        kcal_per_100g = 50.0,
        fats_per_100g=0.1,
    )

    assert updated.name == "Apple"
    assert updated.kcal_per_100g == 50.0
    assert updated.fats_per_100g == 0.1

    # verify if persisted 
    row = session.get(IngredientModel, updated.id)
    assert row.kcal_per_100g == 50.0
    assert row.fats_per_100g == 0.1

def test_update_missing_raises(session):
    repo = IngredientRepo(session)
    with pytest.raises(IngredientNotFound):
        repo.update(123456, name = "doesn't exist")

def test_delete_ok_then_not_found(session, seed_ingredients):
    by_name, _ = seed_ingredients
    target = by_name["Egg"]
    repo = IngredientRepo(session)

    repo.delete(target.id)

    with pytest.raises(IngredientNotFound):
        repo.get_by_id(target.id)

def test_delete_missing_raises(session):
    repo = IngredientRepo(session)
    with pytest.raises(IngredientNotFound):
        repo.delete(42)
