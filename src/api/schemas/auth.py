"""Authentication request and response schemas.

Defines Pydantic models for login, user profile, and token responses.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request body for POST /api/auth/login."""

    email: str = Field(
        description="User email address",
        min_length=3,
        max_length=255,
        examples=["admin@testops.local"],
    )
    password: str = Field(
        description="User password",
        min_length=1,
        max_length=128,
    )


class UserResponse(BaseModel):
    """Public user profile information."""

    id: str = Field(description="Unique user identifier")
    email: str = Field(description="User email address")
    name: str = Field(description="Display name")
    role: str = Field(description="User role (Admin, QA Engineer, etc.)")
    created_at: datetime | None = Field(default=None, description="Account creation timestamp")


class LoginResponse(BaseModel):
    """Response body for successful login."""

    status: str = "success"
    message: str = "Login successful"
    data: UserResponse = Field(description="Authenticated user profile")


class AuthStatusResponse(BaseModel):
    """Response body for GET /api/auth/me."""

    status: str = "success"
    data: UserResponse = Field(description="Current user profile")


class LogoutResponse(BaseModel):
    """Response body for POST /api/auth/logout."""

    status: str = "success"
    message: str = "Logged out successfully"
