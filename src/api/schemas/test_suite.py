"""Test suite request and response schemas.

Defines Pydantic models for test suite listing, detail, and execution.
"""

import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


SuiteStatus = Literal["PENDING", "RUNNING", "PASSED", "FAILED", "BROKEN", "SKIPPED"]


class SuiteStepResponse(BaseModel):
    """Individual test step within a suite."""

    id: str = Field(description="Step identifier")
    name: str = Field(description="Step/assertion name")
    status: str = Field(description="Step status")
    duration_ms: float | None = Field(default=None, description="Step duration in ms")
    error_message: str | None = Field(default=None, description="Error message if failed")


class RunSuiteRequest(BaseModel):
    """Request body for POST /api/test-suites/{id}/run."""

    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )
    browser: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser to use for test execution",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Pytest markers to filter (e.g., ['smoke', 'auth'])",
    )


class TestSuiteResponse(BaseModel):
    """Single test suite response."""

    id: str = Field(description="Unique suite identifier")
    name: str = Field(description="Suite name")
    category: str | None = Field(default=None, description="Suite category")
    project_id: str | None = Field(default=None, description="Associated project ID")
    status: str = Field(description="Current execution status")
    last_run: datetime | None = Field(default=None, description="Last execution timestamp")
    duration: str | None = Field(default=None, description="Last run duration")
    executor: str | None = Field(default=None, description="Who/what triggered the run")
    pass_rate: float = Field(default=0, description="Pass rate percentage")
    steps: list[SuiteStepResponse] | None = Field(default=None, description="Test steps/assertions")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")

    @field_validator("steps", mode="before")
    @classmethod
    def parse_steps(cls, v: Any) -> list[dict] | None:
        """Parse steps from JSON string if stored as text."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v


class TestSuiteListResponse(BaseModel):
    """Response for GET /api/test-suites."""

    status: str = "success"
    data: list[TestSuiteResponse] = Field(description="List of test suites")
    total: int = Field(description="Total suite count")


class TestSuiteDetailResponse(BaseModel):
    """Response for single test suite operations."""

    status: str = "success"
    data: TestSuiteResponse = Field(description="Suite details")
    message: str = ""


class RunSuiteResponse(BaseModel):
    """Response for POST /api/test-suites/{id}/run."""

    status: str = "success"
    message: str = Field(description="Execution status message")
    data: TestSuiteResponse = Field(description="Updated suite with run results")
    execution: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution details (passed, failed, duration, etc.)",
    )
