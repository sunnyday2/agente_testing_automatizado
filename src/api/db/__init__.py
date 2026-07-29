"""Database package for QA Automation Agent.

Provides async SQLite connection management, migration support,
and repository pattern for data access.
"""

from src.api.db.connection import get_db, init_db, close_db

__all__ = ["get_db", "init_db", "close_db"]
