"""Database repository layer.

Provides data access patterns for all application entities.
Each repository encapsulates SQL queries for a specific table/entity.
"""

from src.api.db.repositories.base import BaseRepository

__all__ = ["BaseRepository"]
