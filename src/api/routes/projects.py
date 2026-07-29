"""Projects API routes.

Provides CRUD endpoints for managing QA projects.

Routes:
    GET    /api/projects       — List all projects
    POST   /api/projects       — Create a new project
    PATCH  /api/projects/{id}  — Update a project
    DELETE /api/projects/{id}  — Delete a project
"""

from typing import Any

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.db.connection import get_db
from src.api.middleware.auth_middleware import get_current_user
from src.api.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from src.api.services.project_service import ProjectService
from src.common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List projects",
    description="Retrieve all projects with optional status filter.",
)
async def list_projects(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status (ACTIVE, ARCHIVED, PAUSED)",
    ),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> ProjectListResponse:
    """List all projects.

    Args:
        status_filter: Optional status filter.
        limit: Max results per page.
        offset: Pagination offset.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        List of projects with total count.
    """
    service = ProjectService(db)
    projects, total = await service.list_projects(
        status=status_filter, limit=limit, offset=offset
    )

    return ProjectListResponse(
        data=[ProjectResponse(**p) for p in projects],
        total=total,
    )


@router.post(
    "",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Create a new QA project.",
)
async def create_project(
    body: ProjectCreate,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> ProjectDetailResponse:
    """Create a new project.

    Args:
        body: Project creation data.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        The created project.
    """
    service = ProjectService(db)
    project = await service.create_project(body.model_dump())

    return ProjectDetailResponse(
        data=ProjectResponse(**project),
        message=f"Project '{project['name']}' created successfully",
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Update project",
    description="Update an existing project's fields.",
)
async def update_project(
    project_id: str,
    body: ProjectUpdate,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> ProjectDetailResponse:
    """Update a project by ID.

    Args:
        project_id: The project identifier.
        body: Fields to update.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        The updated project.

    Raises:
        HTTPException: 404 if project not found.
    """
    service = ProjectService(db)
    project = await service.update_project(project_id, body.model_dump(exclude_unset=True))

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )

    return ProjectDetailResponse(
        data=ProjectResponse(**project),
        message="Project updated successfully",
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete project",
    description="Permanently delete a project.",
)
async def delete_project(
    project_id: str,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """Delete a project by ID.

    Args:
        project_id: The project identifier.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Deletion confirmation.

    Raises:
        HTTPException: 404 if project not found.
    """
    service = ProjectService(db)
    deleted = await service.delete_project(project_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )

    return {"status": "success", "message": f"Project '{project_id}' deleted"}
