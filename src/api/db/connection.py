"""Async SQLite database connection management.

Provides connection pooling, initialization, and dependency injection
for FastAPI route handlers.

Usage:
    from src.api.db.connection import get_db

    @router.get("/items")
    async def get_items(db: aiosqlite.Connection = Depends(get_db)):
        async with db.execute("SELECT * FROM items") as cursor:
            rows = await cursor.fetchall()
        return rows
"""

import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

import aiosqlite

from src.common.logging import get_logger

logger = get_logger(__name__)

# Module-level connection pool (single connection for SQLite)
_db_connection: aiosqlite.Connection | None = None
_db_lock = asyncio.Lock()


async def init_db(db_path: str | Path) -> None:
    """Initialize the database connection and enable WAL mode.

    Creates the database file if it doesn't exist.
    Enables WAL (Write-Ahead Logging) for better concurrent read performance.

    Args:
        db_path: Path to the SQLite database file.
    """
    global _db_connection

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    async with _db_lock:
        if _db_connection is not None:
            return

        _db_connection = await aiosqlite.connect(str(db_path))

        # Enable WAL mode for better concurrent read performance
        await _db_connection.execute("PRAGMA journal_mode=WAL")
        # Enable foreign key enforcement
        await _db_connection.execute("PRAGMA foreign_keys=ON")
        # Row factory for dict-like access
        _db_connection.row_factory = aiosqlite.Row

        logger.info("database_initialized", db_path=str(db_path))


async def close_db() -> None:
    """Close the database connection.

    Safe to call multiple times. Should be called during application shutdown.
    """
    global _db_connection

    async with _db_lock:
        if _db_connection is not None:
            await _db_connection.close()
            _db_connection = None
            logger.info("database_connection_closed")


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """FastAPI dependency that yields the database connection.

    Raises:
        RuntimeError: If the database has not been initialized.

    Yields:
        The active aiosqlite connection.
    """
    if _db_connection is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() during application startup."
        )
    yield _db_connection


async def run_migrations(db_path: str | Path, migrations_dir: str | Path) -> list[str]:
    """Apply pending SQL migrations to the database.

    Creates a migrations tracking table if it doesn't exist.
    Applies migrations in filename order (001_, 002_, etc.).
    Records each applied migration to prevent re-application.

    Args:
        db_path: Path to the SQLite database file.
        migrations_dir: Directory containing .sql migration files.

    Returns:
        List of migration filenames that were applied.
    """
    db_path = Path(db_path)
    migrations_dir = Path(migrations_dir)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    applied: list[str] = []

    async with aiosqlite.connect(str(db_path)) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")

        # Create migrations tracking table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

        # Get already-applied migrations
        async with db.execute("SELECT filename FROM _migrations ORDER BY filename") as cursor:
            already_applied = {row[0] for row in await cursor.fetchall()}

        # Find and apply pending migrations
        if not migrations_dir.exists():
            logger.warning("migrations_directory_not_found", path=str(migrations_dir))
            return applied

        migration_files = sorted(
            f for f in migrations_dir.iterdir()
            if f.suffix == ".sql" and f.name not in already_applied
        )

        for migration_file in migration_files:
            logger.info("applying_migration", filename=migration_file.name)
            sql = migration_file.read_text(encoding="utf-8")

            try:
                await db.executescript(sql)
                await db.execute(
                    "INSERT INTO _migrations (filename) VALUES (?)",
                    (migration_file.name,),
                )
                await db.commit()
                applied.append(migration_file.name)
                logger.info("migration_applied", filename=migration_file.name)
            except Exception as exc:
                logger.error(
                    "migration_failed",
                    filename=migration_file.name,
                    error=str(exc),
                )
                raise

    return applied
