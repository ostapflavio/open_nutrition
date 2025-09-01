from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timezone, date, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.infrastructure.repositories.meal_repo import MealRepo
from src.domain.domain import Meal, DataRange
from src.services.errors import ValidationError


def _ensure_utc_bounds(start_date: date, end_date: date) -> DataRange:
    if end_date < start_date:
        raise ValidationError("end_date must be >= start_date")

    start_dt = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date, time.max).replace(tzinfo=timezone.utc)
    return DataRange(start=start_dt, end=end_dt)

def _period_to_date(period: str, today_local: date, tz: ZoneInfo) -> tuple[date, date]:
    """
    Mapper for ?period=this_week|this_month|last_7_days|last_30_days
    All ranges are inclusive in local time.
    """
    if period == "this_week":
        # ISO week: Monday start
        start_local = today_local - timedelta(days=today_local.weekday())
        end_local = today_local
    elif period == "this_month":
        start_local = today_local.replace(day=1)
        end_local = today_local
    elif period == "last_7_days":
        start_local = today_local - timedelta(days=6)
        end_local = today_local
    elif period == "last_30_days":
        start_local = today_local - timedelta(days=29)
        end_local = today_local
    else:
        raise ValidationError("Unsupported period")
    return start_local, end_local

class HistoryService:
    def __init__(self, db: Session):
        self.db = db
        self.meals = MealRepo(db)

    def list_grouped_by_day(
        self,
        *,
        start_date: date,
        end_date: date,
        tz_name: str = "UTC",
        base_url: str = "",  # to build action links
    ):
        # Validate timezone
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            raise ValidationError(f"Invalid timezone: {tz_name}")

        # Compute inclusive UTC bounds for the date interval
        dr = _ensure_utc_bounds(start_date, end_date)

        # Fetch meals in [dr.start, dr.end] (repo should eager-load relations and order by eaten_at)
        meals: list[Meal] = self.meals.list_between(dr.start, dr.end)

        # Group by local day
        grouped: dict[date, list[Meal]] = {}
        total_kcal: float = 0.0

        for m in meals:
            # Normalize potential naive datetimes before converting to local tz
            ea = m.eaten_at
            if ea.tzinfo is None:
                ea = ea.replace(tzinfo=timezone.utc)
            eaten_local = ea.astimezone(tz)

            day = eaten_local.date()
            grouped.setdefault(day, []).append(m)

            kcal = getattr(m, "kcal", None)
            if kcal is not None:
                total_kcal += float(kcal)

        # Build response blocks
        days_out = []
        meal_count = 0

        for day in sorted(grouped.keys(), reverse=True):
            # Optional: ensure meals are ordered by time (latest first)
            day_meals = sorted(grouped[day], key=lambda x: x.eaten_at, reverse=True)

            meals_out = []
            day_kcal = 0.0

            for m in day_meals:
                meal_count += 1

                kcal = getattr(m, "kcal", None)
                if kcal is not None:
                    day_kcal += float(kcal)

                # Normalize and compute local again for payload
                ea = m.eaten_at
                if ea.tzinfo is None:
                    ea = ea.replace(tzinfo=timezone.utc)
                eaten_local = ea.astimezone(tz)

                actions = {}
                if base_url:
                    actions = {
                        "update": f"{base_url}/meals/{m.id}",
                        "delete": f"{base_url}/meals/{m.id}",
                        "star": f"{base_url}/meals/{m.id}/favorite",
                    }

                meals_out.append({
                    "id": m.id,
                    "name": m.name,
                    "eaten_at": ea,                  # UTC, aware
                    "eaten_at_local": eaten_local,   # localized for display
                    "kcal": kcal,
                    "actions": actions,
                })

            days_out.append({
                "day": day,
                "total_kcal": day_kcal if day_kcal > 0 else None,
                "meals": meals_out,
            })

        summary = {
            "day_count": len(days_out),
            "meal_count": meal_count,
            "total_kcal": total_kcal if total_kcal > 0 else None,
        }

        return {
            "range_start": dr.start,
            "range_end": dr.end,
            "timezone": tz.key,
            "days": days_out,
            "summary": summary,
        }