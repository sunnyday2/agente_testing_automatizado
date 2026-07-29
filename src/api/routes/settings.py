"""Settings API routes.

Provides endpoints for reading and updating application settings.

Routes:
    GET   /api/settings — Get all settings
    PATCH /api/settings — Update settings (key-value pairs)
"""

from typing import Any

import aiosqlite
from fastapi import APIRouter, Depends

from src.api.db.connection import get_db
from src.api.middleware.auth_middleware import get_current_user
from src.api.schemas.settings import SettingsResponse, SettingsUpdate
from src.api.services.settings_service import SettingsService
from src.common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get(
    "",
    response_model=SettingsResponse,
    summary="Get settings",
    description="Retrieve all application settings as key-value pairs.",
)
async def get_settings(
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> SettingsResponse:
    """Get all application settings.

    Args:
        db: Database connection.
        _user: Authenticated user.

    Returns:
        All settings as a key-value dict.
    """
    service = SettingsService(db)
    settings = await service.get_all()
    return SettingsResponse(data=settings)


@router.patch(
    "",
    response_model=SettingsResponse,
    summary="Update settings",
    description="Update one or more application settings.",
)
async def update_settings(
    body: SettingsUpdate,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> SettingsResponse:
    """Update application settings.

    Args:
        body: Key-value pairs to update.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        All settings after the update.
    """
    service = SettingsService(db)
    updated = await service.update(body.settings)
    return SettingsResponse(data=updated)
