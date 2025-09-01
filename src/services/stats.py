from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from sqlalchemy.orm import Session
from src.infrastructure.repositories.stats_repo import StatsRepo

from src.domain.domain import DataRange, MacroTotals
from src.services.errors import ValidationError


@dataclass(frozen=True)
class DayCalories:
    day: date
    calories: float

@dataclass(frozen=True)
class MacroPercentages:
    protein_pct: float
    carbs_pct: float
    fat_pct: float

@dataclass(frozen=True)
class StatsResult:
    days: list[DayCalories]
    macro_pct: MacroPercentages
    basis: Literal["kcal", "grams"] # either one or another

class StatsService:
    """
    Computes daily calories and macro split for a date range
    """

    def __init__(self, db: Session):
        self.repo = StatsRepo(db)

    def daily_calories_and_macro_split(
            self,
            dr: DataRange,
            *,
            macro_basis: Literal["kcal", "grams"] = "kcal",
            round_to: int = 1
    ) -> StatsResult:
        start_date = dr.start.date()
        end_date = dr.end.date()

        if end_date < start_date:
            # we double-check here:)
            raise ValidationError("DataRange.end must be >= start")

        rows = self.repo.daily_aggregate(start_date, end_date)
        by_day = {date.fromisoformat(r["day"]): r for r in rows}

        totals = MacroTotals.zero()

        days: list[DayCalories] = []
        cursor = start_date
        while cursor <= end_date:
            r = by_day.get(cursor)
            kcal = float(r["kcal"] if r else 0.0)
            prot_g = float(r["protein_g"] if r else 0.0)
            carb_g = float(r["carbs_g"] if r else 0.0)
            fat_g = float(r["fat_g"] if r else 0.0)

            totals = MacroTotals(
                proteins = totals.proteins + prot_g,
                fats     = totals.fats      + fat_g,
                carbs    = totals.carbs     + carb_g,
                kcal     = totals.kcal      + kcal,
            )

            days.append(DayCalories(day=cursor, calories=round(kcal, round_to)))
            cursor = cursor + timedelta(days=1)

        macro_pct = self._percentages_from_totals(totals, basis=macro_basis, round_to=round_to)
        return StatsResult(days=days, macro_pct=macro_pct, basis=macro_basis)

    @staticmethod
    def _percentages_from_totals(
            totals: MacroTotals,
            *,
            basis: Literal["kcal", "grams"],
            round_to: int,
    ) -> MacroPercentages:
        """
        Convert MacroTotals to percentages that sum to 100.0 exactly
        basis = "kcal": protein * 4, carbs * 4, fat * 4 (industry standard)
        basis = "grams": raw grams
        """
        if basis == "kcal":
            P = totals.proteins * 4.0
            C = totals.carbs * 4.0
            F = totals.fats * 9.0
        else:
            P, C, F = totals.proteins, totals.carbs, totals.fats

        denom = P + C + F
        if denom <= 0:
            return MacroPercentages(0.0, 0.0, 0.0)

        p = round((P / denom) * 100.0, round_to)
        c = round((C / denom) * 100.0, round_to)
        f = round(100.0 - p - c, round_to) # force exact 100.0 total; avoids float drift and rounding missmatch
        return MacroPercentages(p, c, f)