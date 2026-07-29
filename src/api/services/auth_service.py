"""Authentication service for JWT token management and password hashing.

Handles:
- Password hashing and verification via bcrypt
- JWT token creation and validation
- User authentication flow
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

# Password hashing context — bcrypt with auto-migration support
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        plain_password: The plain-text password to hash.

    Returns:
        Bcrypt hashed password string.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash.

    Args:
        plain_password: The plain-text password to verify.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches the hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        user_id: The user's unique identifier.
        email: The user's email address.
        role: The user's role.
        expires_delta: Optional custom expiration time. Defaults to settings.

    Returns:
        Encoded JWT token string.
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(hours=settings.auth.expiry_hours)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.auth.secret,
        algorithm=settings.auth.algorithm,
    )
    return token


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT access token.

    Args:
        token: The encoded JWT token string.

    Returns:
        Decoded token payload dict, or None if invalid/expired.
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.auth.secret,
            algorithms=[settings.auth.algorithm],
        )
        return payload
    except JWTError as exc:
        logger.debug("jwt_decode_failed", error=str(exc))
        return None


async def authenticate_user(
    email: str,
    password: str,
    user_repo,
) -> dict[str, Any] | None:
    """Authenticate a user with email and password.

    Args:
        email: The user's email address.
        password: The plain-text password.
        user_repo: UserRepository instance.

    Returns:
        User record dict if authentication succeeds, None otherwise.
    """
    user = await user_repo.get_by_email(email)
    if user is None:
        logger.info("auth_failed_user_not_found", email=email)
        return None

    if not verify_password(password, user["hashed_password"]):
        logger.info("auth_failed_invalid_password", email=email)
        return None

    logger.info("auth_success", user_id=user["id"], email=email)
    return user
