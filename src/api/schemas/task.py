"""Task (Kanban) request and response schemas.

Defines Pydantic models for task CRUD and move operations.
"""

import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


TaskColumn = Literal["TO DO", "IN PROGRESS", "REVIEW", "DONE"]
TaskPriority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
TaskCategory = Literal["Bug", "Feature", "Test", "Automation", "Infrastructure"]


class TaskCreate(BaseModel):
    """Request body for POST /api/tasks."""

    title: str = Field(
        description="Task title",
        min_length=1,
        max_length=500,
        examples=["Implement login flow tests"],
    )
    description: str | None = Field(
        default=None,
        description="Task description/details",
        max_length=5000,
    )
    category: TaskCategory | None = Field(
        default=None,
        description="Task category",
    )
    business_group: str | None = Field(
        default=None,
        description="Business group/team",
        max_length=100,
    )
    priority: TaskPriority = Field(
        default="MEDIUM",
        description="Task priority",
    )
    column_name: TaskColumn = Field(
        default="TO DO",
        description="Kanban column placement",
    )
    project_id: str | None = Field(
        default=None,
        description="Associated project ID",
    )
    due_date: str | None = Field(
        default=None,
        description="Due date (ISO format)",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Task tags/labels",
    )


class TaskUpdate(BaseModel):
    """Request body for PATCH /api/tasks/{id}."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    category: TaskCategory | None = Field(default=None)
    business_group: str | None = Field(default=None, max_length=100)
    priority: TaskPriority | None = Field(default=None)
    column_name: TaskColumn | None = Field(default=None)
    project_id: str | None = Field(default=None)
    due_date: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)


class TaskMoveRequest(BaseModel):
    """Request body for PATCH /api/tasks/{id}/move."""

    column_name: TaskColumn = Field(
        description="Target Kanban column",
    )


class TaskResponse(BaseModel):
    """Single task response."""

    id: str = Field(description="Unique task identifier")
    title: str = Field(description="Task title")
    description: str | None = Field(default=None)
    category: str | None = Field(default=None)
    business_group: str | None = Field(default=None)
    priority: str = Field(description="Task priority")
    column_name: str = Field(description="Kanban column")
    project_id: str | None = Field(default=None)
    due_date: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    plane_task_id: str | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v: Any) -> list[str] | None:
        """Parse tags from JSON string if needed."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v


class TaskListResponse(BaseModel):
    """Response for GET /api/tasks."""

    status: str = "success"
    data: list[TaskResponse] = Field(description="List of tasks")
    total: int = Field(description="Total task count")


class TaskDetailResponse(BaseModel):
    """Response for single task operations."""

    status: str = "success"
    data: TaskResponse = Field(description="Task details")
    message: str = ""
