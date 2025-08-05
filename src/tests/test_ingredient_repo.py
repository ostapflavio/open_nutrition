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

