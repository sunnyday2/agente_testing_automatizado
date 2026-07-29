"""Stories API routes.

Provides CRUD endpoints for user stories and a seed operation
to trigger RAG indexing into ChromaDB.

Routes:
    GET    /api/stories       — List all stories
    POST   /api/stories       — Create a new story (triggers RAG indexing)
    DELETE /api/stories/{id}  — Delete a story
    POST   /api/stories/seed  — Seed/re-index all stories into ChromaDB
"""

from typing import Any

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.db.connection import get_db
from src.api.middleware.auth_middleware import get_current_user
from src.api.schemas.story import (
    SeedRequest,
    SeedResponse,
    StoryCreate,
    StoryDetailResponse,
    StoryListResponse,
    StoryResponse,
)
from src.api.services.story_service import StoryService
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/stories", tags=["Stories"])


@router.get(
    "",
    response_model=StoryListResponse,
    summary="List stories",
    description="Retrieve all user stories with optional epic, feature, and indexed status filters.",
)
async def list_stories(
    epic: str | None = Query(default=None, description="Filter by epic"),
    feature: str | None = Query(default=None, description="Filter by feature"),
    indexed: bool | None = Query(default=None, description="Filter by indexed status"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> StoryListResponse:
    """List stories with optional filters.

    Args:
        epic: Optional epic filter.
        feature: Optional feature filter.
        indexed: Optional indexed status filter.
        limit: Max results.
        offset: Pagination offset.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        List of stories with total count.
    """
    service = StoryService(db)
    stories, total = await service.list_stories(
        epic=epic,
        feature=feature,
        is_indexed=indexed,
        limit=limit,
        offset=offset,
    )

    return StoryListResponse(
        data=[StoryResponse(**s) for s in stories],
        total=total,
    )


@router.post(
    "",
    response_model=StoryDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create story",
    description="Create a new user story and trigger RAG indexing into ChromaDB.",
)
async def create_story(
    body: StoryCreate,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> StoryDetailResponse:
    """Create a new story and trigger RAG indexing.

    Args:
        body: Story creation data.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        The created story.
    """
    service = StoryService(db)
    story = await service.create_story(body.model_dump())

    indexed_msg = " (indexed in ChromaDB)" if story.get("is_indexed") else " (indexing pending)"
    return StoryDetailResponse(
        data=StoryResponse(**story),
        message=f"Story '{story['title'][:50]}' created{indexed_msg}",
    )


@router.delete(
    "/{story_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete story",
    description="Permanently delete a user story.",
)
async def delete_story(
    story_id: str,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """Delete a story by ID.

    Args:
        story_id: The story identifier.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Deletion confirmation.

    Raises:
        HTTPException: 404 if story not found.
    """
    service = StoryService(db)
    deleted = await service.delete_story(story_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story '{story_id}' not found",
        )

    return {"status": "success", "message": f"Story '{story_id}' deleted"}


@router.post(
    "/seed",
    response_model=SeedResponse,
    summary="Seed stories into ChromaDB",
    description="Index all unindexed stories into ChromaDB. Optionally reset the collection first.",
)
async def seed_stories(
    body: SeedRequest | None = None,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> SeedResponse:
    """Seed all unindexed stories into ChromaDB.

    Args:
        body: Optional seed configuration (reset, collection name).
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Seed operation results.
    """
    if body is None:
        body = SeedRequest()

    settings = get_settings()
    collection_name = body.collection or settings.chromadb.collection_name

    service = StoryService(db)
    indexed_count = await service.seed_stories(
        reset=body.reset,
        collection=body.collection,
    )

    message = (
        f"Seed completed: {indexed_count} stories indexed into '{collection_name}'"
    )
    if body.reset:
        message = f"Collection reset. {message}"

    return SeedResponse(
        message=message,
        stories_indexed=indexed_count,
        collection=collection_name,
    )
