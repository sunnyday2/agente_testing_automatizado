"""Task repository for Kanban board database operations.

Encapsulates all SQL queries related to the tasks table,
including filtering by column, category, and project.
"""

import json
from typing import Any

from src.api.db.repositories.base import BaseRepository, generate_id


class TaskRepository(BaseRepository):
    """Repository for task CRUD and filtering operations."""

    table_name = "tasks"

    async def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task with a generated ID.

        Serializes tags list to JSON for storage.

        Args:
            data: Task fields.

        Returns:
            The created task record.
        """
        data["id"] = generate_id("task")
        if "tags" in data and data["tags"] is not None:
            data["tags"] = json.dumps(data["tags"])
        return await self.create(data)

    async def update_task(self, task_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update a task, serializing tags if present.

        Args:
            task_id: The task ID.
            data: Fields to update.

        Returns:
            Updated task or None if not found.
        """
        if "tags" in data and data["tags"] is not None:
            data["tags"] = json.dumps(data["tags"])
        return await self.update(task_id, data)

    async def move_task(self, task_id: str, column_name: str) -> dict[str, Any] | None:
        """Move a task to a different Kanban column.

        Args:
            task_id: The task ID.
            column_name: Target column name.

        Returns:
            Updated task or None if not found.
        """
        return await self.update(task_id, {"column_name": column_name})

    async def get_by_column(
        self,
        column_name: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get tasks in a specific Kanban column.

        Args:
            column_name: The column to filter by.
            limit: Max results.
            offset: Skip count.

        Returns:
            List of tasks in the column.
        """
        return await self.find_by(
            where="column_name = ?",
            params=(column_name,),
            limit=limit,
            offset=offset,
            order_by="priority DESC, created_at DESC",
        )

    async def get_by_project(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get tasks for a specific project.

        Args:
            project_id: The project ID to filter by.
            limit: Max results.
            offset: Skip count.

        Returns:
            List of tasks for the project.
        """
        return await self.find_by(
            where="project_id = ?",
            params=(project_id,),
            limit=limit,
            offset=offset,
        )

    async def get_by_category(
        self,
        category: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get tasks with a specific category.

        Args:
            category: The category to filter by.
            limit: Max results.
            offset: Skip count.

        Returns:
            List of matching tasks.
        """
        return await self.find_by(
            where="category = ?",
            params=(category,),
            limit=limit,
            offset=offset,
        )

    async def get_filtered(
        self,
        column_name: str | None = None,
        category: str | None = None,
        project_id: str | None = None,
        priority: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Get tasks with multiple optional filters.

        Args:
            column_name: Optional column filter.
            category: Optional category filter.
            project_id: Optional project filter.
            priority: Optional priority filter.
            limit: Max results.
            offset: Skip count.

        Returns:
            Tuple of (tasks list, total matching count).
        """
        conditions: list[str] = []
        params: list[Any] = []

        if column_name:
            conditions.append("column_name = ?")
            params.append(column_name)
        if category:
            conditions.append("category = ?")
            params.append(category)
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
        if priority:
            conditions.append("priority = ?")
            params.append(priority)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        tasks = await self.find_by(
            where=where_clause,
            params=tuple(params),
            limit=limit,
            offset=offset,
            order_by="created_at DESC",
        )

        total = await self.count(where=where_clause, params=tuple(params))

        return tasks, total
