"""Common response schemas used across all API endpoints.

Provides standardized response models for success, error,
pagination, and task status responses.
"""

from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel):
    """Standard success response wrapper.

    Used for simple operation confirmations without complex payloads.
    """

    status: Literal["success"] = "success"
    message: str = Field(description="Human-readable success message")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional additional data",
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response schema.

    Matches the format returned by the global exception handlers.
    """

    error: str = Field(description="Error type/class name")
    message: str = Field(description="Human-readable error description")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context",
    )


class PaginatedResponse(BaseModel):
    """Paginated response wrapper for list endpoints.

    Includes pagination metadata alongside the results.
    """

    items: list[Any] = Field(default_factory=list, description="Page of results")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(default=1, description="Current page number (1-indexed)")
    page_size: int = Field(default=20, description="Number of items per page")
    has_next: bool = Field(default=False, description="Whether more pages exist")

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


class TaskStatusResponse(BaseModel):
    """Response schema for task/execution status queries.

    Used by endpoints that report on async task progress.
    """

    task_id: str = Field(description="Unique task identifier")
    status: Literal["pending", "running", "passed", "failed", "cancelled"] = Field(
        description="Current task execution status"
    )
    message: str = Field(default="", description="Status message or error details")
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Progress from 0.0 to 1.0",
    )
    created_at: datetime | None = Field(default=None, description="When the task was created")
    started_at: datetime | None = Field(default=None, description="When execution started")
    completed_at: datetime | None = Field(default=None, description="When execution finished")
    result: dict[str, Any] = Field(
        default_factory=dict,
        description="Task result data (populated on completion)",
    )


class TestExecutionSummary(BaseModel):
    """Summary of a test execution run."""

    total_tests: int = Field(default=0, description="Total tests executed")
    passed: int = Field(default=0, description="Tests that passed")
    failed: int = Field(default=0, description="Tests that failed")
    skipped: int = Field(default=0, description="Tests that were skipped")
    duration_seconds: float = Field(default=0.0, description="Total execution duration")
    allure_report_url: str = Field(default="", description="URL to the Allure report")


class GenerationSummary(BaseModel):
    """Summary of a test generation operation."""

    scenarios_generated: int = Field(default=0, description="Number of scenarios created")
    tasks_created: int = Field(default=0, description="Number of Plane.so tasks created")
    source_type: Literal["user_story", "site_crawl"] = Field(
        description="Whether generation was from a story or crawl"
    )
    source_identifier: str = Field(
        default="",
        description="Story ID or start URL",
    )
    priority_breakdown: dict[str, int] = Field(
        default_factory=dict,
        description="Count of scenarios by priority (P1, P2, P3)",
    )
