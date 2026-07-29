"""Stats service for aggregating dashboard metrics.

Queries across test_suites, tasks, projects, stories, and events tables
to produce overview stats, velocity data, and failure breakdowns.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import aiosqlite

from src.api.db.repositories.event_repo import EventRepository
from src.common.logging import get_logger

logger = get_logger(__name__)


class StatsService:
    """Aggregation service for dashboard statistics."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize with database connection.

        Args:
            db: Active aiosqlite connection.
        """
        self.db = db
        self.event_repo = EventRepository(db)

    async def get_overview(self) -> dict[str, Any]:
        """Get dashboard overview statistics.

        Queries across multiple tables to produce summary metrics.

        Returns:
            Dict with overview stats fields.
        """
        # Test suite stats
        suite_stats = await self._get_suite_stats()

        # Project count
        async with self.db.execute(
            "SELECT COUNT(*) FROM projects WHERE status = 'ACTIVE'"
        ) as cursor:
            row = await cursor.fetchone()
            active_projects = row[0] if row else 0

        # Story counts
        async with self.db.execute("SELECT COUNT(*) FROM stories") as cursor:
            row = await cursor.fetchone()
            total_stories = row[0] if row else 0

        async with self.db.execute(
            "SELECT COUNT(*) FROM stories WHERE is_indexed = 1"
        ) as cursor:
            row = await cursor.fetchone()
            indexed_stories = row[0] if row else 0

        # Tasks in progress
        async with self.db.execute(
            "SELECT COUNT(*) FROM tasks WHERE column_name = 'IN PROGRESS'"
        ) as cursor:
            row = await cursor.fetchone()
            tasks_in_progress = row[0] if row else 0

        return {
            "total_tests": suite_stats["total"],
            "passed": suite_stats["passed"],
            "failed": suite_stats["failed"],
            "broken": suite_stats["broken"],
            "skipped": suite_stats["skipped"],
            "pass_rate": suite_stats["pass_rate"],
            "total_duration_seconds": suite_stats["total_duration"],
            "active_projects": active_projects,
            "total_stories": total_stories,
            "indexed_stories": indexed_stories,
            "tasks_in_progress": tasks_in_progress,
        }

    async def get_velocity(self, days: int = 30) -> list[dict[str, Any]]:
        """Get daily test execution velocity for the past N days.

        Args:
            days: Number of days to look back.

        Returns:
            List of daily velocity data points.
        """
        # Generate date range
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=days - 1)

        # Query suites that have a last_run timestamp
        query = """
            SELECT 
                DATE(last_run) as run_date,
                COUNT(*) as tests_run,
                SUM(CASE WHEN status = 'PASSED' THEN 1 ELSE 0 END) as tests_passed,
                SUM(CASE WHEN status IN ('FAILED', 'BROKEN') THEN 1 ELSE 0 END) as tests_failed
            FROM test_suites 
            WHERE last_run IS NOT NULL 
              AND DATE(last_run) >= ?
            GROUP BY DATE(last_run)
            ORDER BY run_date ASC
        """
        async with self.db.execute(query, (start_date.isoformat(),)) as cursor:
            rows = await cursor.fetchall()
            run_data = {row[0]: (row[1], row[2], row[3]) for row in rows}

        # Build complete date range with zeros for missing days
        velocity: list[dict[str, Any]] = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.isoformat()
            if date_str in run_data:
                tests_run, tests_passed, tests_failed = run_data[date_str]
            else:
                tests_run, tests_passed, tests_failed = 0, 0, 0

            velocity.append({
                "date": date_str,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
            })

        return velocity

    async def get_failures(self) -> tuple[list[dict[str, Any]], int]:
        """Get failure breakdown by category.

        Groups failed/broken test suites by their category field.

        Returns:
            Tuple of (failure breakdown list, total failures).
        """
        query = """
            SELECT 
                COALESCE(category, 'Uncategorized') as category,
                COUNT(*) as count
            FROM test_suites 
            WHERE status IN ('FAILED', 'BROKEN')
            GROUP BY category
            ORDER BY count DESC
        """
        async with self.db.execute(query) as cursor:
            rows = await cursor.fetchall()

        total_failures = sum(row[1] for row in rows)
        breakdowns: list[dict[str, Any]] = []

        for row in rows:
            category, count = row[0], row[1]
            percentage = round((count / total_failures * 100), 1) if total_failures > 0 else 0.0
            breakdowns.append({
                "category": category,
                "count": count,
                "percentage": percentage,
            })

        return breakdowns, total_failures

    async def get_recent_events(
        self,
        limit: int = 20,
        event_type: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Get recent system events.

        Args:
            limit: Max events to return.
            event_type: Optional type filter.

        Returns:
            Tuple of (events list, total count).
        """
        events = await self.event_repo.get_recent(limit=limit, event_type=event_type)
        total = await self.event_repo.count()
        return events, total

    async def _get_suite_stats(self) -> dict[str, Any]:
        """Get aggregated test suite statistics.

        Returns:
            Dict with total, passed, failed, broken, skipped counts and pass_rate.
        """
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'PASSED' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'BROKEN' THEN 1 ELSE 0 END) as broken,
                SUM(CASE WHEN status = 'SKIPPED' THEN 1 ELSE 0 END) as skipped
            FROM test_suites
        """
        async with self.db.execute(query) as cursor:
            row = await cursor.fetchone()

        total = row[0] if row else 0
        passed = row[1] or 0 if row else 0
        failed = row[2] or 0 if row else 0
        broken = row[3] or 0 if row else 0
        skipped = row[4] or 0 if row else 0

        pass_rate = round((passed / total * 100), 1) if total > 0 else 0.0

        # Sum durations (parsing "X.Ys" format)
        duration_query = "SELECT duration FROM test_suites WHERE duration IS NOT NULL"
        total_duration = 0.0
        async with self.db.execute(duration_query) as cursor:
            rows = await cursor.fetchall()
            for dur_row in rows:
                try:
                    dur_str = dur_row[0].rstrip("s")
                    total_duration += float(dur_str)
                except (ValueError, AttributeError):
                    pass

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "broken": broken,
            "skipped": skipped,
            "pass_rate": pass_rate,
            "total_duration": round(total_duration, 1),
        }
