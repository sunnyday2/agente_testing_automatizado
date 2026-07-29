"""Stats & Reports API routes.

Provides dashboard metrics, velocity charts, failure breakdowns,
and system event feeds.

Routes:
    GET /api/stats/overview   — Dashboard overview metrics
    GET /api/stats/velocity   — Daily test velocity (last N days)
    GET /api/stats/failures   — Failure breakdown by category
    GET /api/stats/events     — Recent system events
    GET /api/reports/analytics — Combined analytics for charts page
"""

from typing import Any

import aiosqlite
from fastapi import APIRouter, Depends, Query

from src.api.db.connection import get_db
from src.api.middleware.auth_middleware import get_current_user
from src.api.schemas.stats import (
    AnalyticsResponse,
    EventsListResponse,
    FailureBreakdown,
    FailuresResponse,
    OverviewResponse,
    OverviewStats,
    SystemEventResponse,
    VelocityDataPoint,
    VelocityResponse,
)
from src.api.services.stats_service import StatsService
from src.common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get(
    "/overview",
    response_model=OverviewResponse,
    summary="Dashboard overview",
    description="Get aggregated metrics for the dashboard overview cards.",
)
async def get_overview(
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> OverviewResponse:
    """Get dashboard overview statistics.

    Args:
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Overview stats including test counts, pass rate, projects, stories.
    """
    service = StatsService(db)
    stats = await service.get_overview()
    return OverviewResponse(data=OverviewStats(**stats))


@router.get(
    "/velocity",
    response_model=VelocityResponse,
    summary="Test velocity",
    description="Get daily test execution volume over the past N days.",
)
async def get_velocity(
    days: int = Query(default=30, ge=7, le=90, description="Number of days to look back"),
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> VelocityResponse:
    """Get daily test velocity chart data.

    Args:
        days: Number of days to include.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Daily velocity data points.
    """
    service = StatsService(db)
    velocity = await service.get_velocity(days=days)
    return VelocityResponse(
        data=[VelocityDataPoint(**v) for v in velocity],
        period_days=days,
    )


@router.get(
    "/failures",
    response_model=FailuresResponse,
    summary="Failure breakdown",
    description="Get failure counts grouped by test suite category.",
)
async def get_failures(
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> FailuresResponse:
    """Get failure breakdown by category.

    Args:
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Failure breakdown with counts and percentages.
    """
    service = StatsService(db)
    breakdowns, total = await service.get_failures()
    return FailuresResponse(
        data=[FailureBreakdown(**b) for b in breakdowns],
        total_failures=total,
    )


@router.get(
    "/events",
    response_model=EventsListResponse,
    summary="Recent events",
    description="Get recent system events for the activity feed.",
)
async def get_events(
    limit: int = Query(default=20, ge=1, le=100, description="Max events to return"),
    event_type: str | None = Query(default=None, description="Filter by event type"),
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> EventsListResponse:
    """Get recent system events.

    Args:
        limit: Maximum events to return.
        event_type: Optional type filter.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Recent system events list.
    """
    service = StatsService(db)
    events, total = await service.get_recent_events(limit=limit, event_type=event_type)
    return EventsListResponse(
        data=[SystemEventResponse(**e) for e in events],
        total=total,
    )


# Analytics endpoint on /api/reports prefix for the frontend reports page
analytics_router = APIRouter(prefix="/api/reports", tags=["Reports"])


@analytics_router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Combined analytics",
    description="Get combined velocity + failures + overview for the reports page charts.",
)
async def get_analytics(
    days: int = Query(default=30, ge=7, le=90),
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> AnalyticsResponse:
    """Get combined analytics data for the reports page.

    Args:
        days: Number of days for velocity data.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Combined velocity, failures, and overview data.
    """
    service = StatsService(db)

    overview = await service.get_overview()
    velocity = await service.get_velocity(days=days)
    breakdowns, _ = await service.get_failures()

    return AnalyticsResponse(
        velocity=[VelocityDataPoint(**v) for v in velocity],
        failures=[FailureBreakdown(**b) for b in breakdowns],
        overview=OverviewStats(**overview),
    )
