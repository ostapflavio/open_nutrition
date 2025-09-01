from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from typing import TypedDict

from sqlalchemy import (
        select,
        func              # func is just a namespace for an SQL function
    )

from sqlalchemy.orm import Session

from src.data.database_models import MealModel, MealEntryModel, IngredientModel

class DayAggRow(TypedDict):
    day: str          # e.g. "2025-08-30"
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float

def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

class StatsRepo:
    """
    Read-model style repo for aggregated nutrition stats.
    """

    def __init__(self, db: Session):
        self.db = db

    def daily_aggregate(
            self,
            start_date: date,
            end_date: date
    ) -> list[DayAggRow]:
        """
        Returns one row per day within [start_date, end_date] that has data:
        - day (YYYY-MM-DD)
        - kcal, protein_g, carbs_g, fat_g (summed per each day)
        Note: Missing days are handled in the service (filled with zero).
        """

        start_dt = _to_utc(datetime.combine(start_date, datetime.min.time()))
        end_dt_excl = _to_utc(datetime.combine(end_date + timedelta(days=1), datetime.min.time()))

        # We'll use the following approach
        # - filter by raw timestamp for index usage
        # - group by func.date()
        day_expr = func.date(MealModel.eaten_at) # collapses all times on the same date in the same group

        stmt = (
            select(
                day_expr.label("day"),
                func.sum(IngredientModel.kcal_per_100g * (MealEntryModel.grams / 100.0)).label("kcal"),
                func.sum(IngredientModel.proteins_per_100g * (MealEntryModel.grams / 100.0)).label("protein_g"),
                func.sum(IngredientModel.carbs_per_100g * (MealEntryModel.grams / 100.0)).label("carbs_g"),
                func.sum(IngredientModel.fats_per_100g * (MealEntryModel.grams / 100.0)).label("fat_g"),
            )
            .join(MealEntryModel, MealEntryModel.meal_id == MealModel.id)
            .join(IngredientModel, IngredientModel.id == MealEntryModel.ingredient_id)
            .where(MealModel.eaten_at >= start_dt, MealModel.eaten_at < end_dt_excl)
            .group_by(day_expr)
            .order_by(day_expr.asc())
        )

        rows = self.db.execute(stmt).mappings().all()
        # rows are MappingResult; convert to TypedDict
        return [
            {
                "day": row["day"],
                "kcal": float(row["kcal"] or 0.0),
                "protein_g": float(row["protein_g"] or 0.0),
                "carbs_g": float(row["carbs_g"] or 0.0),
                "fat_g": float(row["fat_g"] or 0.0),
            }
            for row in rows
        ]