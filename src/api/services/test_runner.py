"""Async Playwright test runner subprocess launcher.

Launches pytest as an async subprocess, captures output, collects
Allure results, and integrates with the Git commit service on success.

Usage:
    from src.api.services.test_runner import TestRunner

    runner = TestRunner()
    result = await runner.run(tags=["smoke"], feature_name="login-flow")
"""

import asyncio
import re
import time
from dataclasses import dataclass
from pathlib import Path

from src.common.exceptions import TestRunnerError, TestTimeoutError
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class TestRunResult:
    """Result of a test execution run."""

    success: bool = False
    exit_code: int = -1
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    tests_total: int = 0
    duration_seconds: float = 0.0
    stdout: str = ""
    stderr: str = ""
    allure_results_dir: str = ""
    git_commit_sha: str = ""


class TestRunner:
    """Manages async test execution via pytest subprocess."""

    def __init__(self) -> None:
        """Initialize the test runner with settings."""
        self._settings = get_settings()
        self._allure_dir = self._settings.test_runner.allure_results_dir
        self._timeout = self._settings.test_runner.timeout // 1000  # ms → seconds
        self._max_retries = self._settings.test_runner.max_retries

    async def run(
        self,
        tags: list[str] | None = None,
        feature_name: str = "unknown",
        test_path: str | None = None,
        extra_args: list[str] | None = None,
    ) -> TestRunResult:
        """Execute a test suite and return results.

        Args:
            tags: Pytest markers to filter tests.
            feature_name: Feature name for Git commit message.
            test_path: Specific test file/directory.
            extra_args: Additional pytest CLI arguments.

        Returns:
            TestRunResult with execution details.
        """
        cmd = self._build_command(tags, test_path, extra_args)

        logger.info(
            "test_runner_starting",
            command=" ".join(cmd),
            feature=feature_name,
            tags=tags,
        )

        start_time = time.time()
        result = await self._execute_subprocess(cmd)
        result.duration_seconds = round(time.time() - start_time, 2)
        self._parse_test_counts(result)

        logger.info(
            "test_runner_completed",
            success=result.success,
            exit_code=result.exit_code,
            passed=result.tests_passed,
            failed=result.tests_failed,
            duration=result.duration_seconds,
        )

        # Retry once on failure if configured
        if not result.success and self._settings.test_runner.retry_on_failure:
            logger.info("test_runner_retrying", feature=feature_name)
            start_time = time.time()
            result = await self._execute_subprocess(cmd)
            result.duration_seconds = round(time.time() - start_time, 2)
            self._parse_test_counts(result)

        # On success, trigger Git commit
        if result.success:
            result.git_commit_sha = self._commit_on_success(
                feature_name=feature_name,
                tests_passed=result.tests_passed,
                tests_total=result.tests_total,
                duration=result.duration_seconds,
            )

        return result

    def _build_command(
        self,
        tags: list[str] | None,
        test_path: str | None,
        extra_args: list[str] | None,
    ) -> list[str]:
        """Build the pytest command line."""
        cmd = [
            "python", "-m", "pytest",
            "--alluredir", self._allure_dir,
            "--tb=short",
            "-v",
        ]

        if tags:
            marker_expr = " or ".join(tags)
            cmd.extend(["-m", marker_expr])

        if test_path:
            cmd.append(test_path)
        else:
            cmd.append(str(PROJECT_ROOT / "tests" / "e2e"))

        if extra_args:
            cmd.extend(extra_args)

        return cmd

    async def _execute_subprocess(self, cmd: list[str]) -> TestRunResult:
        """Execute pytest as an async subprocess."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(PROJECT_ROOT),
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self._timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TestTimeoutError(
                    timeout_seconds=self._timeout,
                    test_suite=" ".join(cmd[3:]),
                )

            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
            exit_code = process.returncode or 0

            return TestRunResult(
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                allure_results_dir=self._allure_dir,
            )

        except (TestTimeoutError, TestRunnerError):
            raise
        except Exception as e:
            raise TestRunnerError(
                exit_code=-1,
                stderr=f"Failed to launch subprocess: {e}",
            ) from e

    def _parse_test_counts(self, result: TestRunResult) -> None:
        """Parse test counts from pytest summary line."""
        output = result.stdout

        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        skipped_match = re.search(r"(\d+) skipped", output)
        error_match = re.search(r"(\d+) error", output)

        if passed_match:
            result.tests_passed = int(passed_match.group(1))
        if failed_match:
            result.tests_failed = int(failed_match.group(1))
        if skipped_match:
            result.tests_skipped = int(skipped_match.group(1))

        errors = int(error_match.group(1)) if error_match else 0
        result.tests_total = (
            result.tests_passed + result.tests_failed + result.tests_skipped + errors
        )

    def _commit_on_success(
        self,
        feature_name: str,
        tests_passed: int,
        tests_total: int,
        duration: float,
    ) -> str:
        """Trigger Git commit after successful test run."""
        try:
            from src.api.services.git_committer import GitCommitService

            service = GitCommitService()
            if not service.is_enabled:
                return ""

            commit_result = service.commit_test_results(
                feature_name=feature_name,
                tests_passed=tests_passed,
                tests_total=tests_total,
                duration_seconds=duration,
            )
            return commit_result.commit_sha if commit_result.success else ""

        except Exception as e:
            logger.warning("git_commit_after_test_failed", error=str(e))
            return ""
