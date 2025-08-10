import pytest
from src.domain.errors import (
    DomainError, Conflict, NotFound, AlreadyExists,
    InvalidIngredient, InvalidMeal, EmptyMeal, InvalidDateRange,
    IngredientNotFound, IngredientAlreadyExists, MealNotFound, FavoriteAlreadyExists,
)

def test_ingredient_not_found_format_and_fields():
    e = IngredientNotFound(identifier=7)
    assert isinstance(e, NotFound)
    assert e.entity == "Ingredient"
    assert e.entity_id == "7"
    s = str(e)
    assert s.startswith("INGREDIENT_NOT_FOUND: ")
    assert "Ingredient not found: 7." in s

def test_ingredient_already_exists_format_and_fields():
    e = IngredientAlreadyExists(identifier="greek-yogurt")
    assert isinstance(e, AlreadyExists)
    assert e.entity == "Ingredient"
    assert e.entity_id == "greek-yogurt"
    assert str(e) == "INGREDIENT_ALREADY_EXISTS: Ingredient already exists: 'greek-yogurt'."

def test_meal_not_found_inheritance_and_message():
    e = MealNotFound(identifier=123)
    assert issubclass(MealNotFound, NotFound)
    assert "Meal not found: 123." in str(e)

def test_favorite_already_exists_inheritance_and_message():
    e = FavoriteAlreadyExists(identifier=5)
    assert issubclass(FavoriteAlreadyExists, AlreadyExists)
    assert "Favorite already exists: 5." in str(e)

def test_custom_message_overrides_default():
    e = IngredientAlreadyExists(message="name must be unique")
    assert str(e) == "INGREDIENT_ALREADY_EXISTS: name must be unique"

def test_chaining_preserves_cause():
    try:
        try:
            raise ValueError("low-level")
        except ValueError as cause:
            raise IngredientAlreadyExists(identifier=1) from cause
    except IngredientAlreadyExists as e:
        assert e.__cause__ is not None
        assert isinstance(e.__cause__, ValueError)

def test_invalid_ingredient_is_domain_error():
    e = InvalidIngredient(message="kcal cannot be negative")
    assert isinstance(e, DomainError)
    assert str(e) == "INVALID_INGREDIENT: kcal cannot be negative"

def test_invalid_meal_and_empty_meal_have_codes():
    assert str(InvalidMeal(message="bad meal")) == "INVALID_MEAL: bad meal"
    assert str(EmptyMeal(message="no items")) == "EMPTY_MEAL: no items"

def test_invalid_date_range_code_and_message():
    e = InvalidDateRange(message="start > end")
    assert str(e) == "INVALID_DATE_RANGE: start > end"

def test_fallback_entity_name_if_not_set():
    class WidgetNotFound(NotFound):
        code = "WIDGET_NOT_FOUND"
        # entity_name intentionally not set to use fallback from class name
    e = WidgetNotFound(identifier=3)
    assert e.entity == "Widget"
    assert "Widget not found: 3." in str(e)
    assert str(e).startswith("WIDGET_NOT_FOUND: ")