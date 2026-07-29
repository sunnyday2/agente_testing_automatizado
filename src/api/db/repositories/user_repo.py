"""User repository for authentication and user management.

Encapsulates all database operations related to user accounts.
"""

from typing import Any

import aiosqlite

from src.api.db.repositories.base import BaseRepository, generate_id


class UserRepository(BaseRepository):
    """Repository for user CRUD operations."""

    table_name = "users"

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Find a user by their email address.

        Args:
            email: The user's email address.

        Returns:
            User record as dict, or None if not found.
        """
        query = "SELECT * FROM users WHERE email = ?"
        async with self.db.execute(query, (email,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create_user(
        self,
        email: str,
        name: str,
        hashed_password: str,
        role: str = "QA Engineer",
    ) -> dict[str, Any]:
        """Create a new user account.

        Args:
            email: User email address (must be unique).
            name: Display name.
            hashed_password: Pre-hashed password (bcrypt).
            role: User role.

        Returns:
            The created user record as dict.
        """
        user_id = generate_id("usr")
        data = {
            "id": user_id,
            "email": email,
            "name": name,
            "hashed_password": hashed_password,
            "role": role,
        }
        return await self.create(data)

    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        """Update a user's password.

        Args:
            user_id: The user's ID.
            hashed_password: New pre-hashed password.

        Returns:
            True if the user was updated, False if not found.
        """
        query = "UPDATE users SET hashed_password = ? WHERE id = ?"
        cursor = await self.db.execute(query, (hashed_password, user_id))
        await self.db.commit()
        return cursor.rowcount > 0

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered.

        Args:
            email: The email address to check.

        Returns:
            True if a user with this email exists.
        """
        query = "SELECT 1 FROM users WHERE email = ? LIMIT 1"
        async with self.db.execute(query, (email,)) as cursor:
            row = await cursor.fetchone()
            return row is not None
