"""User story request and response schemas.

Defines Pydantic models for story CRUD and seed operations.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


StoryFormat = Literal["markdown", "json"]


class StoryCreate(BaseModel):
    """Request body for POST /api/stories."""

    title: str = Field(
        description="Story title",
        min_length=1,
        max_length=500,
        examples=["User can log in with email and password"],
    )
    content: str = Field(
        description="Story content (Markdown or JSON format)",
        min_length=1,
        max_length=50000,
    )
    format: StoryFormat = Field(
        default="markdown",
        description="Content format",
    )
    epic: str | None = Field(
        default=None,
        description="Epic/theme this story belongs to",
        max_length=200,
    )
    feature: str | None = Field(
        default=None,
        description="Feature area",
        max_length=200,
    )
    target_role: str | None = Field(
        default=None,
        description="Target user role (e.g., 'end user', 'admin')",
        max_length=100,
    )


class SeedRequest(BaseModel):
    """Request body for POST /api/stories/seed."""

    reset: bool = Field(
        default=False,
        description="If true, clears existing ChromaDB collection before re-indexing",
    )
    collection: str | None = Field(
        default=None,
        description="Custom collection name (defaults to settings)",
        max_length=100,
    )


class StoryResponse(BaseModel):
    """Single story response."""

    id: str = Field(description="Unique story identifier")
    title: str = Field(description="Story title")
    content: str = Field(description="Story content")
    format: str = Field(description="Content format (markdown or json)")
    epic: str | None = Field(default=None, description="Epic/theme")
    feature: str | None = Field(default=None, description="Feature area")
    target_role: str | None = Field(default=None, description="Target user role")
    is_indexed: bool = Field(default=False, description="Whether story is indexed in ChromaDB")
    test_scenarios_count: int = Field(default=0, description="Number of generated test scenarios")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")


class StoryListResponse(BaseModel):
    """Response for GET /api/stories."""

    status: str = "success"
    data: list[StoryResponse] = Field(description="List of stories")
    total: int = Field(description="Total story count")


class StoryDetailResponse(BaseModel):
    """Response for single story operations."""

    status: str = "success"
    data: StoryResponse = Field(description="Story details")
    message: str = ""


class SeedResponse(BaseModel):
    """Response for POST /api/stories/seed."""

    status: str = "success"
    message: str = Field(description="Seed operation result message")
    stories_indexed: int = Field(default=0, description="Number of stories indexed")
    collection: str = Field(default="", description="Collection name used")
