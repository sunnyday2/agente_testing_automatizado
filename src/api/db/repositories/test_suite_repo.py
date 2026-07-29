"""Test suite repository for database operations.

Encapsulates all SQL queries related to the test_suites table.
"""

import json
from datetime import datetime, timezone
from typing import Any

from src.api.db.repositories.base import BaseRepository, generate_id


class TestSuiteRepository(BaseRepository):
    """Repository for test suite CRUD operations."""

    table_name = "test_suites"

    async def create_suite(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new test suite.

        Args:
            data: Suite fields (name, category, project_id, etc.).

        Returns:
            The created suite record.
        """
        data["id"] = generate_id("suite")
        if "steps" in data and data["steps"] is not None:
            data["steps"] = json.dumps(data["steps"])
        return await self.create(data)

    async def get_by_project(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get test suites for a specific project.

        Args:
            project_id: The project ID.
            limit: Max results.
            offset: Skip count.

        Returns:
            List of suites for the project.
        """
        return await self.find_by(
            where="project_id = ?",
            params=(project_id,),
            limit=limit,
            offset=offset,
            order_by="last_run DESC NULLS LAST, created_at DESC",
        )

    async def get_by_status(
        self,
        status: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get test suites filtered by status.

        Args:
            status: Suite status (PENDING, RUNNING, PASSED, FAILED, etc.).
            limit: Max results.
            offset: Skip count.

        Returns:
            List of matching suites.
        """
        return await self.find_by(
            where="status = ?",
            params=(status,),
            limit=limit,
            offset=offset,
        )

    async def update_status(
        self,
        suite_id: str,
        status: str,
        duration: str | None = None,
        pass_rate: float | None = None,
        last_run: str | None = None,
        executor: str | None = None,
        steps: list[dict] | None = None,
    ) -> dict[str, Any] | None:
        """Update suite status after execution.

        Args:
            suite_id: The suite ID.
            status: New status.
            duration: Execution duration string.
            pass_rate: Pass rate percentage.
            last_run: ISO timestamp of the run.
            executor: Who triggered the run.
            steps: Updated test steps with results.

        Returns:
            Updated suite or None if not found.
        """
        update_fields: dict[str, Any] = {"status": status}

        if duration is not None:
            update_fields["duration"] = duration
        if pass_rate is not None:
            update_fields["pass_rate"] = pass_rate
        if last_run is not None:
            update_fields["last_run"] = last_run
        if executor is not None:
            update_fields["executor"] = executor
        if steps is not None:
            update_fields["steps"] = json.dumps(steps)

        # Build UPDATE directly without adding updated_at (test_suites has no such column)
        set_clause = ", ".join(f"{key} = ?" for key in update_fields)
        values = list(update_fields.values()) + [suite_id]

        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        await self.db.execute(query, values)
        await self.db.commit()

        return await self.get_by_id(suite_id)

    async def get_filtered(
        self,
        project_id: str | None = None,
        status: str | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Get suites with optional filters.

        Args:
            project_id: Optional project filter.
            status: Optional status filter.
            category: Optional category filter.
            limit: Max results.
            offset: Skip count.

        Returns:
            Tuple of (suites list, total count).
        """
        conditions: list[str] = []
        params: list[Any] = []

        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if category:
            conditions.append("category = ?")
            params.append(category)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        suites = await self.find_by(
            where=where_clause,
            params=tuple(params),
            limit=limit,
            offset=offset,
            order_by="last_run DESC NULLS LAST, created_at DESC",
        )

        total = await self.count(where=where_clause, params=tuple(params))

        return suites, total
