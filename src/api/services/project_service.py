"""Project service with business logic.

Handles project creation, updates, health score calculation,
and system event logging for project operations.
"""

from typing import Any

import aiosqlite

from src.api.db.repositories.base import generate_id
from src.api.db.repositories.project_repo import ProjectRepository
from src.common.logging import get_logger

logger = get_logger(__name__)


class ProjectService:
    """Business logic layer for project operations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize with database connection.

        Args:
            db: Active aiosqlite connection.
        """
        self.db = db
        self.repo = ProjectRepository(db)

    async def list_projects(
        self,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List projects with optional status filter.

        Args:
            status: Optional status filter.
            limit: Maximum results.
            offset: Skip count.

        Returns:
            Tuple of (projects list, total count).
        """
        if status:
            projects = await self.repo.get_by_status(status, limit=limit, offset=offset)
            total = await self.repo.count(where="status = ?", params=(status,))
        else:
            projects = await self.repo.get_all(limit=limit, offset=offset)
            total = await self.repo.count()

        return projects, total

    async def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Get a single project by ID.

        Args:
            project_id: The project identifier.

        Returns:
            Project dict or None if not found.
        """
        return await self.repo.get_by_id(project_id)

    async def create_project(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project and log the event.

        Args:
            data: Project creation fields.

        Returns:
            The created project.
        """
        project = await self.repo.create_project(data)
        await self._log_event(
            title=f"Project Created: {project['name']}",
            description=f"New project '{project['name']}' created in {data.get('environment', 'Production')} environment.",
            event_type="success",
        )
        logger.info("project_created", project_id=project["id"], name=project["name"])
        return project

    async def update_project(
        self, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a project and log the event.

        Args:
            project_id: The project ID to update.
            data: Fields to update (only non-None values).

        Returns:
            Updated project or None if not found.
        """
        # Filter out None values
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(project_id)

        project = await self.repo.update(project_id, update_data)
        if project:
            await self._log_event(
                title=f"Project Updated: {project['name']}",
                description=f"Project '{project['name']}' was updated.",
                event_type="info",
            )
            logger.info("project_updated", project_id=project_id)
        return project

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and log the event.

        Args:
            project_id: The project ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        project = await self.repo.get_by_id(project_id)
        if not project:
            return False

        deleted = await self.repo.delete(project_id)
        if deleted:
            await self._log_event(
                title=f"Project Deleted: {project['name']}",
                description=f"Project '{project['name']}' was permanently deleted.",
                event_type="warning",
            )
            logger.info("project_deleted", project_id=project_id, name=project["name"])
        return deleted

    async def _log_event(
        self,
        title: str,
        description: str,
        event_type: str = "info",
    ) -> None:
        """Log a system event to the database.

        Args:
            title: Event title.
            description: Event description.
            event_type: Event type (info, success, warning, error).
        """
        event_id = generate_id("evt")
        try:
            await self.db.execute(
                "INSERT INTO system_events (id, title, description, event_type) VALUES (?, ?, ?, ?)",
                (event_id, title, description, event_type),
            )
            await self.db.commit()
        except Exception as exc:
            logger.warning("event_logging_failed", error=str(exc))
