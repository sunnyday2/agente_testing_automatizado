"""Base repository providing common CRUD operations.

All entity-specific repositories should inherit from BaseRepository
and override the table_name property.

Usage:
    class ProjectRepository(BaseRepository):
        table_name = "projects"

    repo = ProjectRepository(db_connection)
    project = await repo.get_by_id("proj_123")
    all_projects = await repo.get_all()
"""

import uuid
from datetime import datetime, timezone
from typing import Any

import aiosqlite


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix.

    Args:
        prefix: Optional prefix (e.g., 'proj', 'task', 'usr').

    Returns:
        Unique identifier string.
    """
    uid = uuid.uuid4().hex[:12]
    if prefix:
        return f"{prefix}_{uid}"
    return uid


class BaseRepository:
    """Base repository with common CRUD operations for SQLite.

    Subclasses must define `table_name` as a class attribute.

    Attributes:
        table_name: Name of the database table this repository manages.
    """

    table_name: str = ""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize repository with a database connection.

        Args:
            db: Active aiosqlite connection.
        """
        if not self.table_name:
            raise ValueError(
                f"{type(self).__name__} must define 'table_name' class attribute"
            )
        self.db = db

    async def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        """Fetch a single record by its primary key.

        Args:
            record_id: The primary key value.

        Returns:
            Dict representation of the row, or None if not found.
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"  # noqa: S608
        async with self.db.execute(query, (record_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at DESC",
    ) -> list[dict[str, Any]]:
        """Fetch all records with pagination.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            order_by: SQL ORDER BY clause.

        Returns:
            List of dict representations of the rows.
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY {order_by} LIMIT ? OFFSET ?"  # noqa: S608
        async with self.db.execute(query, (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new record.

        Automatically adds 'id' if not present, and 'created_at' timestamp.

        Args:
            data: Dict of column-value pairs to insert.

        Returns:
            The inserted record as a dict.
        """
        if "id" not in data:
            data["id"] = generate_id()
        if "created_at" not in data:
            data["created_at"] = datetime.now(timezone.utc).isoformat()

        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = list(data.values())

        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"  # noqa: S608
        await self.db.execute(query, values)
        await self.db.commit()

        return await self.get_by_id(data["id"]) or data

    async def update(self, record_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update an existing record.

        Automatically sets 'updated_at' if the table has that column.

        Args:
            record_id: The primary key of the record to update.
            data: Dict of column-value pairs to update.

        Returns:
            The updated record as a dict, or None if not found.
        """
        if not data:
            return await self.get_by_id(record_id)

        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        set_clause = ", ".join(f"{key} = ?" for key in data)
        values = list(data.values()) + [record_id]

        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"  # noqa: S608
        await self.db.execute(query, values)
        await self.db.commit()

        return await self.get_by_id(record_id)

    async def delete(self, record_id: str) -> bool:
        """Delete a record by its primary key.

        Args:
            record_id: The primary key of the record to delete.

        Returns:
            True if the record was deleted, False if not found.
        """
        query = f"DELETE FROM {self.table_name} WHERE id = ?"  # noqa: S608
        cursor = await self.db.execute(query, (record_id,))
        await self.db.commit()
        return cursor.rowcount > 0

    async def count(self, where: str = "", params: tuple = ()) -> int:
        """Count records, optionally with a WHERE clause.

        Args:
            where: Optional WHERE clause (without the 'WHERE' keyword).
            params: Parameters for the WHERE clause.

        Returns:
            Number of matching records.
        """
        query = f"SELECT COUNT(*) FROM {self.table_name}"  # noqa: S608
        if where:
            query += f" WHERE {where}"
        async with self.db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def find_by(
        self,
        where: str,
        params: tuple = (),
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at DESC",
    ) -> list[dict[str, Any]]:
        """Find records matching a WHERE clause.

        Args:
            where: SQL WHERE clause (without the 'WHERE' keyword).
            params: Parameters for the WHERE clause.
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            order_by: SQL ORDER BY clause.

        Returns:
            List of matching records as dicts.
        """
        query = (
            f"SELECT * FROM {self.table_name} "  # noqa: S608
            f"WHERE {where} ORDER BY {order_by} LIMIT ? OFFSET ?"
        )
        async with self.db.execute(query, (*params, limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
