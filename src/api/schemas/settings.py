"""Settings request and response schemas.

Defines Pydantic models for application settings CRUD.
"""

from typing import Any

from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    """Response for GET /api/settings."""

    status: str = "success"
    data: dict[str, Any] = Field(
        description="All settings as key-value pairs",
    )


class SettingsUpdate(BaseModel):
    """Request body for PATCH /api/settings."""

    settings: dict[str, Any] = Field(
        description="Key-value pairs to update",
        examples=[{"theme": "dark", "notifications_enabled": "true"}],
    )
