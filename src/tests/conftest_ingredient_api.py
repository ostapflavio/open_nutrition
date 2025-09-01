# tests/conftest.py
import typing as t
import pytest
from fastapi import FastAPI

# Try both common import locations for the router
try:
    from src.api.routers.ingredients import router as ingredients_router, get_service as _get_service_dep
except ImportError:  # fallback
    from src.api.routers.ingredients import router as ingredients_router, get_service as _get_service_dep  # type: ignore


class FakeIngredientService:
    """
    Minimal fake service with only what the router needs for GET /ingredients/{id}.
    Extend this as you implement more endpoints (create/update/delete/list).
    """
    def __init__(self):
        # simple in-memory "DB"
        self._store = {}

    # Convenience: preload or mutate from tests
    def _seed(self, ingredient):
        self._store[ingredient.id] = ingredient

    def get_by_id(self, ingredient_id: int):
        # Import here to avoid hard dependency if your paths differ in project
        from src.domain.errors import IngredientNotFound  # raises when missing
        ing = self._store.get(ingredient_id)
        if not ing:
            raise IngredientNotFound(str(ingredient_id))
        return ing


@pytest.fixture
def fake_service():
    return FakeIngredientService()


@pytest.fixture
def app(fake_service):
    app = FastAPI()
    app.include_router(ingredients_router)

    # FastAPI will call the dependency override with no args, so accept *args/**kwargs.
    def _override_get_service(*_args, **_kwargs):
        return fake_service

    app.dependency_overrides[_get_service_dep] = _override_get_service  # type: ignore
    return app
