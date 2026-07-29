"""Authentication middleware for cookie-based JWT extraction.

Provides a FastAPI dependency that extracts and validates JWT tokens
from httpOnly cookies, injecting the current user into route handlers.

Usage:
    from src.api.middleware.auth_middleware import get_current_user

    @router.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        return {"user": user["email"]}
"""

from typing import Any

import aiosqlite
from fastapi import Cookie, Depends, HTTPException, Request, status

from src.api.db.connection import get_db
from src.api.db.repositories.user_repo import UserRepository
from src.api.services.auth_service import decode_access_token
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


async def get_current_user(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
) -> dict[str, Any]:
    """FastAPI dependency that extracts and validates the current user from JWT cookie.

    Looks for the JWT token in the configured cookie name. Decodes and validates
    the token, then fetches the user from the database to ensure they still exist.

    Args:
        request: The incoming HTTP request.
        db: Database connection (injected).

    Returns:
        User record as dict (without hashed_password).

    Raises:
        HTTPException: 401 if token is missing, invalid, or user not found.
    """
    settings = get_settings()
    cookie_name = settings.auth.cookie_name

    # Extract token from cookie
    token = request.cookies.get(cookie_name)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate JWT
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Verify user still exists in database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Remove sensitive data before returning
    user_data = dict(user)
    user_data.pop("hashed_password", None)
    return user_data


async def get_optional_user(
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
) -> dict[str, Any] | None:
    """FastAPI dependency that optionally extracts the current user.

    Unlike get_current_user, this does not raise an error if no token
    is present. Returns None for unauthenticated requests.

    Args:
        request: The incoming HTTP request.
        db: Database connection (injected).

    Returns:
        User record as dict, or None if not authenticated.
    """
    settings = get_settings()
    cookie_name = settings.auth.cookie_name

    token = request.cookies.get(cookie_name)
    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        return None

    user_data = dict(user)
    user_data.pop("hashed_password", None)
    return user_data
