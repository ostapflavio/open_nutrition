from datetime import datetime, time, timezone, date
from typing import Literal

from fastapi import APIRouter, Query

from src.domain.domain import DataRange
from src.infrastructure.db import db_dependency
from src.services.stats import StatsService, StatsResult
from src.api.schemas import StatsRead, DayCaloriesRead, MacroPercentagesRead
from src.services.errors import ValidationError
router = APIRouter(prefix='/stats', tags=['stats'])

@router.get("/daily-and-macros", response_model=StatsRead)
def get_daily_and_macro_stats(
    db: db_dependency,
    start_date: date = Query(..., description ="Inclusive start (YYYY-MM-DD)"),
    end_date: date = Query(..., description = "Inclusive end (YYYY-MM-DD)"),
    macro_basis: Literal["kcal", "grams"] = Query("kcal", description = "Pie basis"),
):
    try:
        dr = DataRange(
            start=datetime.combine(start_date, time.min, tzinfo=timezone.utc),
            end=datetime.combine(end_date, time.max, tzinfo=timezone.utc),
        )
    except ValueError as e:
        raise ValidationError(str(e))

    svc = StatsService(db)
    result: StatsResult = svc.daily_calories_and_macro_split(dr, macro_basis=macro_basis)

    return StatsRead(
        days=[DayCaloriesRead(day=d.day, calories=d.calories) for d in result.days],
        macro_pct=MacroPercentagesRead(**result.macro_pct.__dict__),
        basis=result.basis
    )