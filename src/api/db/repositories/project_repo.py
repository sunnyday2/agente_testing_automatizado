"""Project repository for database operations.

Encapsulates all SQL queries related to the projects table.
"""

from typing import Any

from src.api.db.repositories.base import BaseRepository, generate_id


class ProjectRepository(BaseRepository):
    """Repository for project CRUD operations."""

    table_name = "projects"

    async def create_project(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project with a generated ID.

        Args:
            data: Project fields (name, subtitle, environment, visibility).

        Returns:
            The created project record.
        """
        data["id"] = generate_id("proj")
        return await self.create(data)

    async def get_by_status(
        self,
        status: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get projects filtered by status.

        Args:
            status: Project status (ACTIVE, ARCHIVED, PAUSED).
            limit: Maximum results.
            offset: Skip count.

        Returns:
            List of matching projects.
        """
        return await self.find_by(
            where="status = ?",
            params=(status,),
            limit=limit,
            offset=offset,
        )

    async def update_health_score(self, project_id: str, score: int) -> dict[str, Any] | None:
        """Update a project's health score.

        Args:
            project_id: The project ID.
            score: New health score (0-100).

        Returns:
            Updated project, or None if not found.
        """
        score = max(0, min(100, score))
        return await self.update(project_id, {"health_score": score})
