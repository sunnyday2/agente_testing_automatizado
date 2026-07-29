#!/usr/bin/env python3
"""Database migration runner for QA Automation Agent.

Applies pending SQL migrations from src/api/db/migrations/ to the
configured SQLite database. This script is standalone and avoids
importing the full application to prevent dependency issues.

Usage:
    python scripts/migrate.py
    python scripts/migrate.py --db-path ./data/qa_agent.db
    python scripts/migrate.py --migrations-dir ./src/api/db/migrations
"""

import argparse
import asyncio
import sys
from pathlib import Path

import aiosqlite

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "qa_agent.db"
DEFAULT_MIGRATIONS_DIR = PROJECT_ROOT / "src" / "api" / "db" / "migrations"


async def run_migrations(db_path: Path, migrations_dir: Path) -> list[str]:
    """Apply pending SQL migrations to the database.

    Creates a migrations tracking table if it doesn't exist.
    Applies migrations in filename order (001_, 002_, etc.).

    Args:
        db_path: Path to the SQLite database file.
        migrations_dir: Directory containing .sql migration files.

    Returns:
        List of migration filenames that were applied.
    """
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
            print(f"ERROR: Migrations directory not found: {migrations_dir}")
            return applied

        migration_files = sorted(
            f for f in migrations_dir.iterdir()
            if f.suffix == ".sql" and f.name not in already_applied
        )

        for migration_file in migration_files:
            print(f"  Applying: {migration_file.name}...")
            sql = migration_file.read_text(encoding="utf-8")

            try:
                await db.executescript(sql)
                await db.execute(
                    "INSERT INTO _migrations (filename) VALUES (?)",
                    (migration_file.name,),
                )
                await db.commit()
                applied.append(migration_file.name)
            except Exception as exc:
                print(f"  ERROR: Migration failed: {exc}")
                raise

    return applied


async def main(db_path: Path, migrations_dir: Path) -> int:
    """Run database migrations.

    Args:
        db_path: Path to the SQLite database file.
        migrations_dir: Directory containing .sql migration files.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    print(f"Database: {db_path}")
    print(f"Migrations directory: {migrations_dir}")
    print("-" * 60)

    if not migrations_dir.exists():
        print(f"ERROR: Migrations directory not found: {migrations_dir}")
        return 1

    migration_files = sorted(f for f in migrations_dir.iterdir() if f.suffix == ".sql")
    print(f"Found {len(migration_files)} migration file(s)")

    try:
        applied = await run_migrations(db_path, migrations_dir)
    except Exception as exc:
        print(f"\nERROR: Migration failed: {exc}")
        return 1

    if applied:
        print(f"\nApplied {len(applied)} migration(s):")
        for filename in applied:
            print(f"  ✓ {filename}")
    else:
        print("\nNo pending migrations. Database is up to date.")

    print("-" * 60)
    print("Done.")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Apply database migrations for QA Automation Agent"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=DEFAULT_MIGRATIONS_DIR,
        help=f"Migrations directory (default: {DEFAULT_MIGRATIONS_DIR})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit_code = asyncio.run(main(args.db_path, args.migrations_dir))
    sys.exit(exit_code)
