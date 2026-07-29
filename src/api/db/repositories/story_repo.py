"""Story repository for database operations.

Encapsulates all SQL queries related to the stories table,
including CRUD and indexing status management.
"""

from typing import Any

from src.api.db.repositories.base import BaseRepository, generate_id


class StoryRepository(BaseRepository):
    """Repository for story CRUD and indexing operations."""

    table_name = "stories"

    async def create_story(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new story with a generated ID.

        Args:
            data: Story fields (title, content, format, epic, feature, target_role).

        Returns:
            The created story record.
        """
        data["id"] = generate_id("story")
        return await self.create(data)

    async def mark_indexed(
        self,
        story_id: str,
        is_indexed: bool = True,
        test_scenarios_count: int = 0,
    ) -> dict[str, Any] | None:
        """Mark a story as indexed (or un-indexed) in ChromaDB.

        Args:
            story_id: The story ID.
            is_indexed: Whether the story has been indexed.
            test_scenarios_count: Number of test scenarios generated.

        Returns:
            Updated story or None if not found.
        """
        query = (
            "UPDATE stories SET is_indexed = ?, test_scenarios_count = ? WHERE id = ?"
        )
        await self.db.execute(query, (is_indexed, test_scenarios_count, story_id))
        await self.db.commit()
        return await self.get_by_id(story_id)

    async def get_unindexed(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get stories that have not been indexed yet.

        Args:
            limit: Maximum results.

        Returns:
            List of unindexed stories.
        """
        return await self.find_by(
            where="is_indexed = 0",
            params=(),
            limit=limit,
            order_by="created_at ASC",
        )

    async def get_indexed(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get stories that have been indexed.

        Args:
            limit: Maximum results.

        Returns:
            List of indexed stories.
        """
        return await self.find_by(
            where="is_indexed = 1",
            params=(),
            limit=limit,
            order_by="created_at DESC",
        )

    async def get_by_epic(self, epic: str, limit: int = 100) -> list[dict[str, Any]]:
        """Get stories by epic.

        Args:
            epic: The epic name to filter by.
            limit: Maximum results.

        Returns:
            List of stories in the epic.
        """
        return await self.find_by(
            where="epic = ?",
            params=(epic,),
            limit=limit,
        )

    async def get_filtered(
        self,
        epic: str | None = None,
        feature: str | None = None,
        is_indexed: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Get stories with optional filters.

        Args:
            epic: Optional epic filter.
            feature: Optional feature filter.
            is_indexed: Optional indexed status filter.
            limit: Max results.
            offset: Skip count.

        Returns:
            Tuple of (stories list, total count).
        """
        conditions: list[str] = []
        params: list[Any] = []

        if epic:
            conditions.append("epic = ?")
            params.append(epic)
        if feature:
            conditions.append("feature = ?")
            params.append(feature)
        if is_indexed is not None:
            conditions.append("is_indexed = ?")
            params.append(1 if is_indexed else 0)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        stories = await self.find_by(
            where=where_clause,
            params=tuple(params),
            limit=limit,
            offset=offset,
            order_by="created_at DESC",
        )

        total = await self.count(where=where_clause, params=tuple(params))

        return stories, total
