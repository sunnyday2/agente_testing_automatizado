"""Task service with business logic.

Handles task CRUD, Kanban column moves, Plane.so sync (when configured),
and system event logging.
"""

from typing import Any

import aiosqlite

from src.api.db.repositories.base import generate_id
from src.api.db.repositories.task_repo import TaskRepository
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


class TaskService:
    """Business logic layer for task operations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize with database connection.

        Args:
            db: Active aiosqlite connection.
        """
        self.db = db
        self.repo = TaskRepository(db)

    async def list_tasks(
        self,
        column_name: str | None = None,
        category: str | None = None,
        project_id: str | None = None,
        priority: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List tasks with optional filters.

        Args:
            column_name: Filter by Kanban column.
            category: Filter by task category.
            project_id: Filter by project.
            priority: Filter by priority.
            limit: Maximum results.
            offset: Pagination offset.

        Returns:
            Tuple of (tasks list, total count).
        """
        return await self.repo.get_filtered(
            column_name=column_name,
            category=category,
            project_id=project_id,
            priority=priority,
            limit=limit,
            offset=offset,
        )

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Get a single task by ID.

        Args:
            task_id: The task identifier.

        Returns:
            Task dict or None if not found.
        """
        return await self.repo.get_by_id(task_id)

    async def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task and optionally sync to Plane.so.

        Args:
            data: Task creation fields.

        Returns:
            The created task.
        """
        task = await self.repo.create_task(data)

        # Attempt Plane.so sync if configured
        plane_task_id = await self._sync_to_plane_create(task)
        if plane_task_id:
            task = await self.repo.update_task(task["id"], {"plane_task_id": plane_task_id})

        await self._log_event(
            title=f"Task Created: {task['title']}",
            description=f"New task in '{task.get('column_name', 'TO DO')}' column.",
            event_type="info",
        )
        logger.info("task_created", task_id=task["id"], title=task["title"])
        return task

    async def update_task(
        self, task_id: str, data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a task.

        Args:
            task_id: The task ID to update.
            data: Fields to update (only non-None values).

        Returns:
            Updated task or None if not found.
        """
        # Filter out None values
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.repo.get_by_id(task_id)

        task = await self.repo.update_task(task_id, update_data)
        if task:
            logger.info("task_updated", task_id=task_id)
        return task

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: The task ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        task = await self.repo.get_by_id(task_id)
        if not task:
            return False

        deleted = await self.repo.delete(task_id)
        if deleted:
            await self._log_event(
                title=f"Task Deleted: {task['title']}",
                description=f"Task removed from '{task.get('column_name', 'unknown')}' column.",
                event_type="info",
            )
            logger.info("task_deleted", task_id=task_id, title=task["title"])
        return deleted

    async def move_task(self, task_id: str, column_name: str) -> dict[str, Any] | None:
        """Move a task to a different Kanban column.

        Logs the move event and syncs to Plane.so if configured.

        Args:
            task_id: The task ID to move.
            column_name: Target column name.

        Returns:
            Updated task or None if not found.
        """
        task = await self.repo.get_by_id(task_id)
        if not task:
            return None

        old_column = task.get("column_name", "unknown")
        updated = await self.repo.move_task(task_id, column_name)

        if updated:
            await self._sync_to_plane_move(updated, column_name)
            await self._log_event(
                title=f"Task Moved: {updated['title']}",
                description=f"Moved from '{old_column}' to '{column_name}'.",
                event_type="info",
            )
            logger.info(
                "task_moved",
                task_id=task_id,
                from_column=old_column,
                to_column=column_name,
            )
        return updated

    async def _sync_to_plane_create(self, task: dict[str, Any]) -> str | None:
        """Sync task creation to Plane.so if configured.

        Args:
            task: The created task.

        Returns:
            Plane.so task ID if sync succeeded, None otherwise.
        """
        settings = get_settings()
        if not settings.plane.api_key or not settings.plane.project_id:
            return None

        try:
            from src.api.services.plane_client import PlaneClient

            client = PlaneClient()
            result = await client.create_issue(
                name=task["title"],
                description=task.get("description", ""),
                priority=task.get("priority", "medium").lower(),
            )
            return result.get("id") if result else None
        except Exception as exc:
            logger.warning("plane_sync_create_failed", error=str(exc), task_id=task["id"])
            return None

    async def _sync_to_plane_move(self, task: dict[str, Any], column_name: str) -> None:
        """Sync task column move to Plane.so if configured.

        Args:
            task: The task being moved.
            column_name: Target column name.
        """
        settings = get_settings()
        plane_task_id = task.get("plane_task_id")
        if not plane_task_id or not settings.plane.api_key:
            return

        # Map column names to Plane.so states
        column_to_state = {
            "TO DO": "TODO",
            "IN PROGRESS": "DOING",
            "REVIEW": "DOING",
            "DONE": "FINISHED",
        }
        state = column_to_state.get(column_name)
        if not state:
            return

        try:
            from src.api.services.plane_client import PlaneClient

            client = PlaneClient()
            await client.update_issue_state(plane_task_id, state)
        except Exception as exc:
            logger.warning(
                "plane_sync_move_failed",
                error=str(exc),
                task_id=task["id"],
                plane_task_id=plane_task_id,
            )

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
