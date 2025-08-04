from src.domain import IngredientSource, Ingredient 
from src.infrastructure.repositories.ingredient_repo import IngredientRepo 
from src.domain.errors import IngredientNotFound 

def test_create_and_get_by_id(session):
    repo = IngredientRepo(session)

    ingredient = repo.create(
            name = 'rice',
            kcal_per_100g=399,
            carbs_per_100g=69.3, 
            proteins_per_100g=16.9,
            fats_per_100g=6.9,
            source=IngredientSource.CUSTOM
    )

    result = repo.get_by_id(ingredient.id)
    assert result.name == 'rice'
    assert result.kcal_per_100g == 399


