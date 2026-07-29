"""System event repository for activity feed and audit log.

Encapsulates queries for the system_events table.
"""

from typing import Any

from src.api.db.repositories.base import BaseRepository, generate_id


class EventRepository(BaseRepository):
    """Repository for system event operations."""

    table_name = "system_events"

    async def create_event(
        self,
        title: str,
        description: str | None = None,
        event_type: str = "info",
    ) -> dict[str, Any]:
        """Create a new system event.

        Args:
            title: Event title.
            description: Event description/details.
            event_type: Event type (info, success, warning, error).

        Returns:
            The created event record.
        """
        data = {
            "id": generate_id("evt"),
            "title": title,
            "description": description,
            "event_type": event_type,
        }
        return await self.create(data)

    async def get_recent(
        self,
        limit: int = 20,
        event_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get recent system events ordered by newest first.

        Args:
            limit: Maximum events to return.
            event_type: Optional filter by event type.

        Returns:
            List of recent events.
        """
        if event_type:
            return await self.find_by(
                where="event_type = ?",
                params=(event_type,),
                limit=limit,
                order_by="timestamp DESC",
            )
        return await self.get_all(limit=limit, order_by="timestamp DESC")

    async def get_count_by_type(self) -> dict[str, int]:
        """Get event counts grouped by type.

        Returns:
            Dict mapping event_type to count.
        """
        query = "SELECT event_type, COUNT(*) as count FROM system_events GROUP BY event_type"
        async with self.db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}

    async def get_events_since(
        self,
        since_timestamp: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get events since a given timestamp.

        Args:
            since_timestamp: ISO timestamp to filter from.
            limit: Maximum results.

        Returns:
            List of events since the timestamp.
        """
        return await self.find_by(
            where="timestamp >= ?",
            params=(since_timestamp,),
            limit=limit,
            order_by="timestamp DESC",
        )
