"""Settings repository for key-value configuration store.

Encapsulates queries for the settings table which stores
application-level configuration as key-value pairs.
"""

from datetime import datetime, timezone
from typing import Any

import aiosqlite


class SettingsRepository:
    """Repository for settings key-value store operations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize with database connection.

        Args:
            db: Active aiosqlite connection.
        """
        self.db = db

    async def get_all(self) -> dict[str, Any]:
        """Get all settings as a dictionary.

        Returns:
            Dict of all key-value settings.
        """
        query = "SELECT key, value FROM settings ORDER BY key"
        async with self.db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}

    async def get_by_key(self, key: str) -> str | None:
        """Get a single setting value by key.

        Args:
            key: The setting key.

        Returns:
            Setting value, or None if not found.
        """
        query = "SELECT value FROM settings WHERE key = ?"
        async with self.db.execute(query, (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def upsert(self, key: str, value: str) -> None:
        """Insert or update a setting.

        Args:
            key: The setting key.
            value: The setting value.
        """
        now = datetime.now(timezone.utc).isoformat()
        query = """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """
        await self.db.execute(query, (key, value, now))
        await self.db.commit()

    async def upsert_many(self, settings: dict[str, Any]) -> None:
        """Insert or update multiple settings.

        Args:
            settings: Dict of key-value pairs to upsert.
        """
        now = datetime.now(timezone.utc).isoformat()
        query = """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """
        for key, value in settings.items():
            await self.db.execute(query, (key, str(value), now))
        await self.db.commit()

    async def delete(self, key: str) -> bool:
        """Delete a setting by key.

        Args:
            key: The setting key to delete.

        Returns:
            True if the setting was deleted, False if not found.
        """
        query = "DELETE FROM settings WHERE key = ?"
        cursor = await self.db.execute(query, (key,))
        await self.db.commit()
        return cursor.rowcount > 0
