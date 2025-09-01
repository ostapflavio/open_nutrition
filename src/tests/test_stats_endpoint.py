import datetime as dt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the actual router under test  :contentReference[oaicite:16]{index=16}
from src.api.routers.stats import router as stats_router
from src.services.stats import StatsResult, DayCalories, MacroPercentages  # :contentReference[oaicite:17]{index=17}


def utc_date(y, m, d):
    return dt.date(y, m, d)


@pytest.fixture
def app(monkeypatch):
    # Build a tiny app with just the stats router  :contentReference[oaicite:18]{index=18}
    app = FastAPI()
    app.include_router(stats_router)

    # Override the db dependency to avoid touching a real DB  :contentReference[oaicite:19]{index=19}
    from src.api.routers import stats as stats_module

    def fake_db():
        yield None

    app.dependency_overrides[stats_module.db_dependency] = fake_db

    # Monkeypatch StatsService.daily_calories_and_macro_split to return a canned result  :contentReference[oaicite:20]{index=20}
    from src.services import stats as svc_module

    def fake_daily(dr, macro_basis="kcal", round_to=1):
        return StatsResult(
            days=[
                DayCalories(day=utc_date(2025, 8, 28), calories=600.0),
                DayCalories(day=utc_date(2025, 8, 29), calories=0.0),
                DayCalories(day=utc_date(2025, 8, 30), calories=900.0),
            ],
            macro_pct=MacroPercentages(protein_pct=22.9, carbs_pct=34.4, fat_pct=42.7),
            basis=macro_basis,
        )

    monkeypatch.setattr(svc_module.StatsService, "daily_calories_and_macro_split", staticmethod(fake_daily))
    return app


def test_daily_and_macros_happy_path(app):
    client = TestClient(app)
    resp = client.get(
        "/stats/daily-and-macros",
        params={
            "start_date": "2025-08-28",
            "end_date": "2025-08-30",
            "macro_basis": "kcal",
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    # Response model shape  :contentReference[oaicite:21]{index=21}
    assert "days" in body and "macro_pct" in body and "basis" in body
    assert body["basis"] == "kcal"

    # Days array + values mapped from service result  :contentReference[oaicite:22]{index=22}
    assert [d["day"] for d in body["days"]] == ["2025-08-28", "2025-08-29", "2025-08-30"]
    assert [d["calories"] for d in body["days"]] == [600.0, 0.0, 900.0]

    mp = body["macro_pct"]
    assert mp == {"protein_pct": 22.9, "carbs_pct": 34.4, "fat_pct": 42.7}


def test_macro_basis_validation(app):
    client = TestClient(app)
    # Literal["kcal","grams"] should reject other values at request-validation level  :contentReference[oaicite:23]{index=23}
    resp = client.get(
        "/stats/daily-and-macros",
        params={"start_date": "2025-08-28", "end_date": "2025-08-30", "macro_basis": "percent"},
    )
    assert resp.status_code == 422  # FastAPI validation error for invalid enum literal


def test_date_order_validation_bubbles_up(app):
    client = TestClient(app)
    # DataRange enforces end >= start; router wraps construction and turns ValueError into ValidationError  :contentReference[oaicite:24]{index=24}
    resp = client.get(
        "/stats/daily-and-macros",
        params={"start_date": "2025-08-30", "end_date": "2025-08-28", "macro_basis": "kcal"},
    )
    # Depending on your global exception handler for ValidationError, this will typically be 400 or 422.
    assert resp.status_code in (400, 422)
