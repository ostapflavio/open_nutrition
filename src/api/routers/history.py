from datetime import date, datetime, timezone
from typing import Optional, Literal

from fastapi import APIRouter, Query
from starlette import status

from src.infrastructure.db import db_dependency
from src.services.history import HistoryService, _ensure_utc_bounds, _period_to_date
from src.api.schemas import HistoryRead

router = APIRouter(prefix="/history", tags=["history"])

PeriodLiteral = Literal["this_week", "this_month", "last_7_days", "last_30_days"]

@router.get("", response_model=HistoryRead, status_code=status.HTTP_200_OK)
def get_history(
    db: db_dependency,
    start_date: Optional[date] = Query(None, description="Inclusive start (YYYY-MM-DD)"),
    end_date: Optional[date]   = Query(None, description="Inclusive end (YYYY-MM-DD)"),
    period: Optional[PeriodLiteral] = Query(
        None,
        description="Optional convenience period. Ignored if start_date/end_date provided."
    ),
    tz: str = Query("UTC", description="IANA timezone for grouping days (e.g., Europe/Chisinau)"),
):
    """
    Returns meals grouped by local day for the given inclusive interval.
    Either provide start_date & end_date, or a `period` like 'this_week'.
    Interval must include at least one calendar day.
    """
    svc = HistoryService(db)

    if start_date and end_date:
        # use explicit dates
        pass
    else:
        if not period:
            # default: last_7_days
            period = "last_7_days"
        from zoneinfo import ZoneInfo
        from datetime import datetime, timedelta
        now_local = datetime.now(ZoneInfo(tz)).date()
        start_date, end_date = _period_to_date(period, now_local, ZoneInfo(tz))

    result = svc.list_grouped_by_day(
        start_date=start_date,
        end_date=end_date,
        tz_name=tz,
        # if you deploy behind a known base URL, set here so 'actions' are populated
        base_url="",  # e.g., base_url="https://api.yourapp.com"
    )
    return result
