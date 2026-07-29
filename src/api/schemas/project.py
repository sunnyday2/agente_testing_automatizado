"""Project request and response schemas.

Defines Pydantic models for project CRUD operations.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ProjectStatus = Literal["ACTIVE", "ARCHIVED", "PAUSED"]
ProjectVisibility = Literal["Public", "Private"]
ProjectEnvironment = Literal["Production", "Staging", "Development"]


class ProjectCreate(BaseModel):
    """Request body for POST /api/projects."""

    name: str = Field(
        description="Project name",
        min_length=1,
        max_length=255,
        examples=["My E-Commerce App"],
    )
    subtitle: str | None = Field(
        default=None,
        description="Short project description",
        max_length=500,
    )
    environment: ProjectEnvironment = Field(
        default="Production",
        description="Target environment",
    )
    visibility: ProjectVisibility = Field(
        default="Public",
        description="Project visibility",
    )


class ProjectUpdate(BaseModel):
    """Request body for PATCH /api/projects/{id}."""

    name: str | None = Field(
        default=None,
        description="Updated project name",
        min_length=1,
        max_length=255,
    )
    subtitle: str | None = Field(
        default=None,
        description="Updated description",
        max_length=500,
    )
    environment: ProjectEnvironment | None = Field(
        default=None,
        description="Updated environment",
    )
    visibility: ProjectVisibility | None = Field(
        default=None,
        description="Updated visibility",
    )
    status: ProjectStatus | None = Field(
        default=None,
        description="Updated status",
    )


class ProjectResponse(BaseModel):
    """Single project response."""

    id: str = Field(description="Unique project identifier")
    name: str = Field(description="Project name")
    subtitle: str | None = Field(default=None, description="Short description")
    environment: str = Field(description="Target environment")
    visibility: str = Field(description="Visibility setting")
    status: str = Field(description="Project status")
    health_score: int = Field(description="Health score (0-100)")
    integrations: dict | None = Field(default=None, description="Active integrations")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")


class ProjectListResponse(BaseModel):
    """Response for GET /api/projects."""

    status: str = "success"
    data: list[ProjectResponse] = Field(description="List of projects")
    total: int = Field(description="Total project count")


class ProjectDetailResponse(BaseModel):
    """Response for single project operations."""

    status: str = "success"
    data: ProjectResponse = Field(description="Project details")
    message: str = ""
