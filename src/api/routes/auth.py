"""Authentication API routes.

Provides login, logout, and current user profile endpoints.
Uses httpOnly cookies for JWT token storage.

Routes:
    POST /api/auth/login   — Authenticate and set session cookie
    POST /api/auth/logout  — Clear session cookie
    GET  /api/auth/me      — Get current authenticated user profile
"""

from typing import Any

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.api.db.connection import get_db
from src.api.db.repositories.user_repo import UserRepository
from src.api.middleware.auth_middleware import get_current_user
from src.api.schemas.auth import (
    AuthStatusResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    UserResponse,
)
from src.api.services.auth_service import authenticate_user, create_access_token
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate with email and password. Sets an httpOnly JWT cookie on success.",
)
async def login(
    body: LoginRequest,
    response: Response,
    db: aiosqlite.Connection = Depends(get_db),
) -> LoginResponse:
    """Authenticate a user and set JWT cookie.

    Args:
        body: Login credentials (email + password).
        response: FastAPI response object for setting cookies.
        db: Database connection.

    Returns:
        Login response with user profile.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    user_repo = UserRepository(db)
    user = await authenticate_user(body.email, body.password, user_repo)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"],
    )

    # Set httpOnly cookie
    settings = get_settings()
    response.set_cookie(
        key=settings.auth.cookie_name,
        value=token,
        httponly=settings.auth.cookie_httponly,
        secure=settings.auth.cookie_secure,
        samesite=settings.auth.cookie_samesite,
        max_age=settings.auth.expiry_hours * 3600,
        path="/",
    )

    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user.get("created_at"),
    )

    logger.info("user_logged_in", user_id=user["id"], email=user["email"])

    return LoginResponse(data=user_response)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="User logout",
    description="Clear the JWT session cookie.",
)
async def logout(
    response: Response,
    _user: dict[str, Any] = Depends(get_current_user),
) -> LogoutResponse:
    """Clear the JWT cookie to log the user out.

    Args:
        response: FastAPI response object for clearing cookies.
        _user: Current user (validates they are authenticated).

    Returns:
        Logout confirmation.
    """
    settings = get_settings()
    response.delete_cookie(
        key=settings.auth.cookie_name,
        path="/",
        httponly=settings.auth.cookie_httponly,
        secure=settings.auth.cookie_secure,
        samesite=settings.auth.cookie_samesite,
    )

    logger.info("user_logged_out", user_id=_user["id"])

    return LogoutResponse()


@router.get(
    "/me",
    response_model=AuthStatusResponse,
    summary="Current user profile",
    description="Get the profile of the currently authenticated user.",
)
async def get_me(
    user: dict[str, Any] = Depends(get_current_user),
) -> AuthStatusResponse:
    """Return the current authenticated user's profile.

    Args:
        user: Current user from JWT cookie (injected by dependency).

    Returns:
        Current user profile.
    """
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user.get("created_at"),
    )

    return AuthStatusResponse(data=user_response)
