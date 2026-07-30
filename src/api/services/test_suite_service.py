"""Test suite service with execution logic.

Handles suite listing, status management, and delegates actual test
execution to the existing TestRunner service.
"""

from datetime import datetime, timezone
from typing import Any

import aiosqlite

from src.api.db.repositories.base import generate_id
from src.api.db.repositories.test_suite_repo import TestSuiteRepository
from src.api.services.test_runner import TestRunner, TestRunResult
from src.common.logging import get_logger

logger = get_logger(__name__)


class TestSuiteService:
    """Business logic layer for test suite operations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        """Initialize with database connection.

        Args:
            db: Active aiosqlite connection.
        """
        self.db = db
        self.repo = TestSuiteRepository(db)
        self.runner = TestRunner()

    async def list_suites(
        self,
        project_id: str | None = None,
        status: str | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """List test suites with optional filters.

        Args:
            project_id: Optional project filter.
            status: Optional status filter.
            category: Optional category filter.
            limit: Max results.
            offset: Skip count.

        Returns:
            Tuple of (suites list, total count).
        """
        return await self.repo.get_filtered(
            project_id=project_id,
            status=status,
            category=category,
            limit=limit,
            offset=offset,
        )

    async def get_suite(self, suite_id: str) -> dict[str, Any] | None:
        """Get a single test suite by ID.

        Args:
            suite_id: The suite identifier.

        Returns:
            Suite dict or None if not found.
        """
        return await self.repo.get_by_id(suite_id)

    async def register_suite(self, suite_data: dict[str, Any]) -> dict[str, Any] | None:
        """Register a new test suite in the database.

        Args:
            suite_data: Dict with name, category, test_path.

        Returns:
            Created suite dict.
        """
        from datetime import datetime, timezone

        suite_id = generate_id("suite")
        now = datetime.now(timezone.utc).isoformat()

        await self.db.execute(
            """INSERT OR IGNORE INTO test_suites (id, name, category, status, pass_rate, steps, test_path, created_at)
               VALUES (?, ?, ?, 'PENDING', 0.0, '[]', ?, ?)""",
            (suite_id, suite_data["name"], suite_data["category"], suite_data.get("test_path"), now),
        )
        await self.db.commit()

        return await self.repo.get_by_id(suite_id)

    async def run_suite(
        self,
        suite_id: str,
        headless: bool = True,
        browser: str = "chromium",
        tags: list[str] | None = None,
        executor: str = "UI",
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        """Trigger test execution for a suite.

        Updates the suite status to RUNNING, delegates execution to TestRunner,
        then updates the status based on results.

        Args:
            suite_id: The suite ID to execute.
            headless: Run browser headlessly.
            browser: Browser to use.
            tags: Pytest markers to filter.
            executor: Who triggered the run.

        Returns:
            Tuple of (updated suite, execution details dict).
            Suite is None if not found.
        """
        suite = await self.repo.get_by_id(suite_id)
        if suite is None:
            return None, {}

        # Mark as running
        now = datetime.now(timezone.utc).isoformat()
        await self.repo.update_status(
            suite_id=suite_id,
            status="RUNNING",
            last_run=now,
            executor=executor,
        )

        logger.info(
            "test_suite_execution_starting",
            suite_id=suite_id,
            name=suite["name"],
            executor=executor,
        )

        # Build extra args for the runner
        extra_args: list[str] = []
        if headless:
            extra_args.append("--headed=false")
        if browser != "chromium":
            extra_args.extend(["--browser", browser])

        # Determine tags from suite category or request
        run_tags = tags or []
        if not run_tags and suite.get("category"):
            run_tags = [suite["category"].lower()]

        # Execute via TestRunner
        try:
            result: TestRunResult = await self.runner.run(
                tags=run_tags if run_tags else None,
                feature_name=suite["name"],
                test_path=suite.get("test_path"),
                extra_args=extra_args if extra_args else None,
            )
        except Exception as exc:
            logger.error(
                "test_suite_execution_failed",
                suite_id=suite_id,
                error=str(exc),
            )
            # Mark as failed
            updated_suite = await self.repo.update_status(
                suite_id=suite_id,
                status="FAILED",
                duration="0s",
                pass_rate=0.0,
                steps=[{
                    "id": "error",
                    "name": "Execution Error",
                    "status": "FAILED",
                    "duration_ms": 0,
                    "error_message": str(exc),
                }],
            )
            execution_details = {
                "success": False,
                "error": str(exc),
                "tests_total": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "duration_seconds": 0,
            }
            await self._log_event(
                title=f"Suite Failed: {suite['name']}",
                description=f"Execution error: {str(exc)[:200]}",
                event_type="error",
            )
            return updated_suite, execution_details

        # Determine final status
        if result.success:
            final_status = "PASSED"
        elif result.tests_failed > 0:
            final_status = "FAILED"
        else:
            final_status = "BROKEN"

        # Calculate pass rate
        pass_rate = 0.0
        if result.tests_total > 0:
            pass_rate = round((result.tests_passed / result.tests_total) * 100, 1)

        # Format duration
        duration_str = f"{result.duration_seconds:.1f}s"

        # Build steps from result output
        steps = self._build_steps_from_result(result)

        # Update suite with results
        updated_suite = await self.repo.update_status(
            suite_id=suite_id,
            status=final_status,
            duration=duration_str,
            pass_rate=pass_rate,
            steps=steps,
        )

        execution_details = {
            "success": result.success,
            "tests_total": result.tests_total,
            "tests_passed": result.tests_passed,
            "tests_failed": result.tests_failed,
            "tests_skipped": result.tests_skipped,
            "duration_seconds": result.duration_seconds,
            "exit_code": result.exit_code,
            "allure_results_dir": result.allure_results_dir,
            "git_commit_sha": result.git_commit_sha,
        }

        event_type = "success" if result.success else "error"
        await self._log_event(
            title=f"Suite {'Passed' if result.success else 'Failed'}: {suite['name']}",
            description=(
                f"{result.tests_passed}/{result.tests_total} tests passed "
                f"in {duration_str}. Pass rate: {pass_rate}%"
            ),
            event_type=event_type,
        )

        logger.info(
            "test_suite_execution_completed",
            suite_id=suite_id,
            status=final_status,
            passed=result.tests_passed,
            failed=result.tests_failed,
            duration=result.duration_seconds,
        )

        return updated_suite, execution_details

    def _build_steps_from_result(self, result: TestRunResult) -> list[dict[str, Any]]:
        """Build step entries from TestRunResult for storage.

        Args:
            result: The test run result.

        Returns:
            List of step dicts representing test outcomes.
        """
        steps: list[dict[str, Any]] = []

        if result.tests_passed > 0:
            steps.append({
                "id": "passed",
                "name": f"{result.tests_passed} test(s) passed",
                "status": "PASSED",
                "duration_ms": (result.duration_seconds * 1000) / max(result.tests_total, 1),
                "error_message": None,
            })

        if result.tests_failed > 0:
            steps.append({
                "id": "failed",
                "name": f"{result.tests_failed} test(s) failed",
                "status": "FAILED",
                "duration_ms": None,
                "error_message": result.stderr[:500] if result.stderr else None,
            })

        if result.tests_skipped > 0:
            steps.append({
                "id": "skipped",
                "name": f"{result.tests_skipped} test(s) skipped",
                "status": "SKIPPED",
                "duration_ms": None,
                "error_message": None,
            })

        return steps

    async def create_suite(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new test suite.

        Args:
            data: Suite creation fields.

        Returns:
            The created suite.
        """
        suite = await self.repo.create_suite(data)
        logger.info("test_suite_created", suite_id=suite["id"], name=suite["name"])
        return suite

    async def _log_event(
        self,
        title: str,
        description: str,
        event_type: str = "info",
    ) -> None:
        """Log a system event to the database.

        Args:
            title: Event title.
            description: Event description.
            event_type: Event type.
        """
        event_id = generate_id("evt")
        try:
            await self.db.execute(
                "INSERT INTO system_events (id, title, description, event_type) VALUES (?, ?, ?, ?)",
                (event_id, title, description, event_type),
            )
            await self.db.commit()
        except Exception as exc:
            logger.warning("event_logging_failed", error=str(exc))
