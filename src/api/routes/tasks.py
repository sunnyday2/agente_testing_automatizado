"""Tasks (Kanban) API routes.

Provides CRUD endpoints and move operation for Kanban board tasks.

Routes:
    GET    /api/tasks           — List tasks with optional filters
    POST   /api/tasks           — Create a new task
    PATCH  /api/tasks/{id}      — Update a task
    DELETE /api/tasks/{id}      — Delete a task
    PATCH  /api/tasks/{id}/move — Move task to a different column
"""

from typing import Any

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.db.connection import get_db
from src.api.middleware.auth_middleware import get_current_user
from src.api.schemas.task import (
    TaskCreate,
    TaskDetailResponse,
    TaskListResponse,
    TaskMoveRequest,
    TaskResponse,
    TaskUpdate,
)
from src.api.services.task_service import TaskService
from src.common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List tasks",
    description="Retrieve tasks with optional column, category, project, and priority filters.",
)
async def list_tasks(
    column: str | None = Query(default=None, description="Filter by Kanban column"),
    category: str | None = Query(default=None, description="Filter by category"),
    project_id: str | None = Query(default=None, description="Filter by project ID"),
    priority: str | None = Query(default=None, description="Filter by priority"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> TaskListResponse:
    """List tasks with optional filters.

    Args:
        column: Optional column filter.
        category: Optional category filter.
        project_id: Optional project filter.
        priority: Optional priority filter.
        limit: Max results per page.
        offset: Pagination offset.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        List of tasks with total count.
    """
    service = TaskService(db)
    tasks, total = await service.list_tasks(
        column_name=column,
        category=category,
        project_id=project_id,
        priority=priority,
        limit=limit,
        offset=offset,
    )

    return TaskListResponse(
        data=[TaskResponse(**t) for t in tasks],
        total=total,
    )


@router.post(
    "",
    response_model=TaskDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new Kanban task.",
)
async def create_task(
    body: TaskCreate,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> TaskDetailResponse:
    """Create a new task.

    Args:
        body: Task creation data.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        The created task.
    """
    service = TaskService(db)
    task = await service.create_task(body.model_dump())

    return TaskDetailResponse(
        data=TaskResponse(**task),
        message=f"Task '{task['title']}' created in '{task.get('column_name', 'TO DO')}'",
    )


@router.patch(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Update task",
    description="Update an existing task's fields.",
)
async def update_task(
    task_id: str,
    body: TaskUpdate,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> TaskDetailResponse:
    """Update a task by ID.

    Args:
        task_id: The task identifier.
        body: Fields to update.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        The updated task.

    Raises:
        HTTPException: 404 if task not found.
    """
    service = TaskService(db)
    task = await service.update_task(task_id, body.model_dump(exclude_unset=True))

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    return TaskDetailResponse(
        data=TaskResponse(**task),
        message="Task updated successfully",
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete task",
    description="Permanently delete a task.",
)
async def delete_task(
    task_id: str,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """Delete a task by ID.

    Args:
        task_id: The task identifier.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Deletion confirmation.

    Raises:
        HTTPException: 404 if task not found.
    """
    service = TaskService(db)
    deleted = await service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    return {"status": "success", "message": f"Task '{task_id}' deleted"}


@router.patch(
    "/{task_id}/move",
    response_model=TaskDetailResponse,
    summary="Move task",
    description="Move a task to a different Kanban column.",
)
async def move_task(
    task_id: str,
    body: TaskMoveRequest,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> TaskDetailResponse:
    """Move a task to a different column.

    Args:
        task_id: The task identifier.
        body: Target column.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        The updated task in its new column.

    Raises:
        HTTPException: 404 if task not found.
    """
    service = TaskService(db)
    task = await service.move_task(task_id, body.column_name)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    return TaskDetailResponse(
        data=TaskResponse(**task),
        message=f"Task moved to '{body.column_name}'",
    )
