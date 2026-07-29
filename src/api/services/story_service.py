"""Story service with RAG indexing integration.

Handles story CRUD, triggers RAG pipeline for embedding stories into
ChromaDB, and manages the seed operation for bulk indexing.
"""

from typing import Any

import aiosqlite

from src.api.db.repositories.base import generate_id
from src.api.db.repositories.story_repo import StoryRepository
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


class StoryService:
    """Business logic layer for story operations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize with database connection.

        Args:
            db: Active aiosqlite connection.
        """
        self.db = db
        self.repo = StoryRepository(db)

    async def list_stories(
        self,
        epic: str | None = None,
        feature: str | None = None,
        is_indexed: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List stories with optional filters.

        Args:
            epic: Optional epic filter.
            feature: Optional feature filter.
            is_indexed: Optional indexed status filter.
            limit: Max results.
            offset: Skip count.

        Returns:
            Tuple of (stories list, total count).
        """
        return await self.repo.get_filtered(
            epic=epic,
            feature=feature,
            is_indexed=is_indexed,
            limit=limit,
            offset=offset,
        )

    async def get_story(self, story_id: str) -> dict[str, Any] | None:
        """Get a single story by ID.

        Args:
            story_id: The story identifier.

        Returns:
            Story dict or None if not found.
        """
        return await self.repo.get_by_id(story_id)

    async def create_story(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new story and trigger RAG indexing.

        Args:
            data: Story creation fields.

        Returns:
            The created story (with is_indexed updated if indexing succeeds).
        """
        story = await self.repo.create_story(data)

        # Attempt to index in ChromaDB
        indexed = await self._index_story(story)
        if indexed:
            story = await self.repo.mark_indexed(story["id"], is_indexed=True)

        await self._log_event(
            title=f"Story Created: {story['title'][:50]}",
            description=(
                f"Story '{story['title']}' added. "
                f"{'Indexed in ChromaDB.' if story.get('is_indexed') else 'Pending indexing.'}"
            ),
            event_type="success" if story.get("is_indexed") else "info",
        )

        logger.info(
            "story_created",
            story_id=story["id"],
            title=story["title"],
            indexed=story.get("is_indexed", False),
        )
        return story

    async def delete_story(self, story_id: str) -> bool:
        """Delete a story.

        Args:
            story_id: The story ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        story = await self.repo.get_by_id(story_id)
        if not story:
            return False

        deleted = await self.repo.delete(story_id)
        if deleted:
            await self._log_event(
                title=f"Story Deleted: {story['title'][:50]}",
                description=f"Story '{story['title']}' was removed.",
                event_type="info",
            )
            logger.info("story_deleted", story_id=story_id, title=story["title"])
        return deleted

    async def seed_stories(
        self,
        reset: bool = False,
        collection: str | None = None,
    ) -> int:
        """Seed all unindexed stories into ChromaDB.

        Optionally resets the collection first, then indexes all stories
        that haven't been indexed yet (or all stories if reset=True).

        Args:
            reset: Whether to clear the collection before seeding.
            collection: Custom collection name (overrides settings).

        Returns:
            Number of stories successfully indexed.
        """
        settings = get_settings()
        collection_name = collection or settings.chromadb.collection_name

        logger.info(
            "story_seed_starting",
            reset=reset,
            collection=collection_name,
        )

        # If reset, mark all stories as unindexed and clear collection
        if reset:
            await self._reset_collection(collection_name)
            # Mark all stories as unindexed
            await self.db.execute("UPDATE stories SET is_indexed = 0, test_scenarios_count = 0")
            await self.db.commit()

        # Get all unindexed stories
        unindexed = await self.repo.get_unindexed(limit=1000)
        if not unindexed:
            logger.info("story_seed_no_pending", collection=collection_name)
            return 0

        indexed_count = 0
        for story in unindexed:
            success = await self._index_story(story, collection_name=collection_name)
            if success:
                await self.repo.mark_indexed(story["id"], is_indexed=True)
                indexed_count += 1

        await self._log_event(
            title=f"Stories Seeded: {indexed_count} indexed",
            description=(
                f"Seed operation completed. {indexed_count}/{len(unindexed)} stories "
                f"indexed into collection '{collection_name}'."
            ),
            event_type="success",
        )

        logger.info(
            "story_seed_completed",
            indexed=indexed_count,
            total=len(unindexed),
            collection=collection_name,
        )

        return indexed_count

    async def _index_story(
        self,
        story: dict[str, Any],
        collection_name: str | None = None,
    ) -> bool:
        """Index a single story into ChromaDB via the RAG pipeline.

        Uses the existing VectorStoreManager and embedding pipeline.

        Args:
            story: The story record to index.
            collection_name: Optional collection name override.

        Returns:
            True if indexing succeeded, False otherwise.
        """
        try:
            from langchain_core.documents import Document
            from src.rag.vectorstore import VectorStoreManager

            # Build a LangChain Document from the story
            metadata = {
                "story_id": story["id"],
                "title": story["title"],
                "format": story.get("format", "markdown"),
            }
            if story.get("epic"):
                metadata["epic"] = story["epic"]
            if story.get("feature"):
                metadata["feature"] = story["feature"]
            if story.get("target_role"):
                metadata["target_role"] = story["target_role"]

            doc = Document(
                page_content=story["content"],
                metadata=metadata,
            )

            # Use VectorStoreManager to add to ChromaDB
            manager = VectorStoreManager(
                collection_name=collection_name,
            )
            manager.add_documents([doc])

            logger.debug(
                "story_indexed_in_chromadb",
                story_id=story["id"],
                title=story["title"],
            )
            return True

        except Exception as exc:
            logger.warning(
                "story_indexing_failed",
                story_id=story["id"],
                error=str(exc),
            )
            return False

    async def _reset_collection(self, collection_name: str) -> None:
        """Reset (delete and recreate) a ChromaDB collection.

        Args:
            collection_name: The collection to reset.
        """
        try:
            from src.rag.vectorstore import VectorStoreManager

            manager = VectorStoreManager(collection_name=collection_name)
            manager.reset_collection()
            logger.info("collection_reset", collection=collection_name)
        except Exception as exc:
            logger.warning("collection_reset_failed", error=str(exc))

    async def _log_event(
        self,
        title: str,
        description: str,
        event_type: str = "info",
    ) -> None:
        """Log a system event.

        Args:
            title: Event title.
            description: Event description.
            event_type: Event type.
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
