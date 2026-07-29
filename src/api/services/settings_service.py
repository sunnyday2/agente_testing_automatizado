"""Settings service for application configuration management.

Provides read/write operations for the key-value settings store.
"""

from typing import Any

import aiosqlite

from src.api.db.repositories.settings_repo import SettingsRepository
from src.common.logging import get_logger

logger = get_logger(__name__)


class SettingsService:
    """Business logic layer for settings operations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize with database connection.

        Args:
            db: Active aiosqlite connection.
        """
        self.db = db
        self.repo = SettingsRepository(db)

    async def get_all(self) -> dict[str, Any]:
        """Get all application settings.

        Returns:
            Dict of all key-value settings.
        """
        return await self.repo.get_all()

    async def get(self, key: str) -> str | None:
        """Get a single setting value.

        Args:
            key: The setting key.

        Returns:
            Setting value or None.
        """
        return await self.repo.get_by_key(key)

    async def update(self, settings: dict[str, Any]) -> dict[str, Any]:
        """Update multiple settings.

        Args:
            settings: Dict of key-value pairs to update.

        Returns:
            All settings after update.
        """
        await self.repo.upsert_many(settings)
        logger.info("settings_updated", keys=list(settings.keys()))
        return await self.repo.get_all()
