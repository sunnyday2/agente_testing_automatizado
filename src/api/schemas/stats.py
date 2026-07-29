"""Stats and reports response schemas.

Defines Pydantic models for dashboard overview, velocity charts,
and failure breakdown analytics.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class OverviewStats(BaseModel):
    """Dashboard overview statistics."""

    total_tests: int = Field(default=0, description="Total test suites")
    passed: int = Field(default=0, description="Suites in PASSED status")
    failed: int = Field(default=0, description="Suites in FAILED status")
    broken: int = Field(default=0, description="Suites in BROKEN status")
    skipped: int = Field(default=0, description="Suites in SKIPPED status")
    pass_rate: float = Field(default=0.0, description="Overall pass rate percentage")
    total_duration_seconds: float = Field(default=0.0, description="Total execution time")
    active_projects: int = Field(default=0, description="Projects with ACTIVE status")
    total_stories: int = Field(default=0, description="Total user stories")
    indexed_stories: int = Field(default=0, description="Stories indexed in ChromaDB")
    tasks_in_progress: int = Field(default=0, description="Tasks in IN PROGRESS column")


class OverviewResponse(BaseModel):
    """Response for GET /api/stats/overview."""

    status: str = "success"
    data: OverviewStats = Field(description="Dashboard overview metrics")


class VelocityDataPoint(BaseModel):
    """Single data point for velocity chart."""

    date: str = Field(description="Date (YYYY-MM-DD)")
    tests_run: int = Field(default=0, description="Total tests run that day")
    tests_passed: int = Field(default=0, description="Tests passed that day")
    tests_failed: int = Field(default=0, description="Tests failed that day")


class VelocityResponse(BaseModel):
    """Response for GET /api/stats/velocity."""

    status: str = "success"
    data: list[VelocityDataPoint] = Field(description="Daily velocity data points")
    period_days: int = Field(default=30, description="Number of days covered")


class FailureBreakdown(BaseModel):
    """Single category in the failure breakdown."""

    category: str = Field(description="Failure category")
    count: int = Field(default=0, description="Number of failures in this category")
    percentage: float = Field(default=0.0, description="Percentage of total failures")


class FailuresResponse(BaseModel):
    """Response for GET /api/stats/failures."""

    status: str = "success"
    data: list[FailureBreakdown] = Field(description="Failure breakdown by category")
    total_failures: int = Field(default=0, description="Total failure count")


class SystemEventResponse(BaseModel):
    """Single system event."""

    id: str = Field(description="Event identifier")
    title: str = Field(description="Event title")
    description: str | None = Field(default=None, description="Event details")
    event_type: str = Field(description="Event type (info, success, warning, error)")
    timestamp: datetime | None = Field(default=None, description="When the event occurred")


class EventsListResponse(BaseModel):
    """Response for GET /api/stats/events."""

    status: str = "success"
    data: list[SystemEventResponse] = Field(description="Recent system events")
    total: int = Field(default=0, description="Total event count")


class AnalyticsResponse(BaseModel):
    """Combined analytics for the reports page."""

    status: str = "success"
    velocity: list[VelocityDataPoint] = Field(description="Velocity chart data")
    failures: list[FailureBreakdown] = Field(description="Failure breakdown")
    overview: OverviewStats = Field(description="Summary metrics")
