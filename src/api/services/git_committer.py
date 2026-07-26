"""Automatic Git commit service for successful test runs.

Creates structured Git commits after test suites pass, staging only
test-related artifacts. Supports three modes: commit-only,
commit-and-push, or disabled.

Flow:
    1. Test runner completes with exit code 0 (PASSED)
    2. GitCommitService.commit_test_results() is called
    3. Files matching stage_patterns are staged
    4. Structured commit message is created with feature, timestamp, summary
    5. If mode == "commit-and-push": push to configured remote/branch
    6. Commit SHA and metadata logged for audit trail

Usage:
    from src.api.services.git_committer import GitCommitService

    service = GitCommitService()
    result = service.commit_test_results(
        feature_name="login-flow",
        tests_passed=12,
        tests_total=12,
        duration_seconds=45.2,
    )
"""

import glob
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from git import Actor, InvalidGitRepositoryError, Repo
from git.exc import GitCommandError

from src.common.exceptions import GitCommitError
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


@dataclass
class CommitResult:
    """Result of a Git commit operation.

    Attributes:
        success: Whether the commit was created successfully.
        commit_sha: The SHA hash of the created commit.
        branch: The branch the commit was made on.
        files_staged: Number of files staged for the commit.
        pushed: Whether the commit was pushed to remote.
        message: The commit message used.
        timestamp: When the commit was created.
        error: Error message if the operation failed.
    """

    success: bool = False
    commit_sha: str = ""
    branch: str = ""
    files_staged: int = 0
    pushed: bool = False
    message: str = ""
    timestamp: str = ""
    error: str = ""


class GitCommitService:
    """Service for automatically committing test artifacts on success.

    Only commits when tests pass. Uses structured commit messages
    and stages only test-related files matching configured patterns.
    """

    def __init__(self, repo_path: str | Path | None = None) -> None:
        """Initialize the Git commit service.

        Args:
            repo_path: Path to the Git repository root.
                Defaults to the project root directory.

        Raises:
            GitCommitError: If the path is not a valid Git repository.
        """
        self._settings = get_settings()
        self._git_config = self._settings.git

        if repo_path is None:
            repo_path = Path(__file__).resolve().parent.parent.parent.parent

        try:
            self._repo = Repo(str(repo_path))
        except InvalidGitRepositoryError as e:
            raise GitCommitError(
                operation="init",
                reason=f"Not a valid Git repository: {repo_path}",
            ) from e

    @property
    def is_enabled(self) -> bool:
        """Check if Git auto-commit is enabled."""
        return self._git_config.enabled and self._git_config.mode != "disabled"

    @property
    def current_branch(self) -> str:
        """Get the current branch name."""
        try:
            return str(self._repo.active_branch)
        except TypeError:
            # Detached HEAD state
            return "HEAD"

    def commit_test_results(
        self,
        feature_name: str,
        tests_passed: int,
        tests_total: int,
        duration_seconds: float,
        extra_files: list[str] | None = None,
    ) -> CommitResult:
        """Create a Git commit after successful test execution.

        Only proceeds if:
        - Git auto-commit is enabled
        - All tests passed (tests_passed == tests_total)
        - There are files to stage

        Args:
            feature_name: Name of the feature being tested.
            tests_passed: Number of tests that passed.
            tests_total: Total number of tests executed.
            duration_seconds: Total test execution duration in seconds.
            extra_files: Additional file paths to stage beyond configured patterns.

        Returns:
            CommitResult with operation details and status.
        """
        # Guard: check if enabled
        if not self.is_enabled:
            logger.info("git_commit_disabled")
            return CommitResult(error="Git auto-commit is disabled")

        # Guard: only commit on full pass
        if tests_passed != tests_total:
            logger.info(
                "git_commit_skipped_tests_not_all_passed",
                passed=tests_passed,
                total=tests_total,
            )
            return CommitResult(
                error=f"Not all tests passed ({tests_passed}/{tests_total})"
            )

        logger.info(
            "git_commit_starting",
            feature=feature_name,
            tests_passed=tests_passed,
            mode=self._git_config.mode,
        )

        try:
            # Stage files
            staged_count = self._stage_files(extra_files)

            if staged_count == 0:
                logger.info("git_commit_skipped_nothing_to_stage")
                return CommitResult(error="No files to stage")

            # Build commit message
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            summary = f"{tests_passed} tests passed in {duration_seconds:.1f}s"

            commit_message = self._git_config.commit_message_template.format(
                feature=feature_name,
                timestamp=timestamp,
                summary=summary,
            )

            # Create the commit
            author = Actor(
                self._git_config.author_name,
                self._git_config.author_email,
            )
            commit = self._repo.index.commit(
                commit_message,
                author=author,
                committer=author,
            )

            commit_sha = str(commit.hexsha)
            branch = self.current_branch

            logger.info(
                "git_commit_created",
                sha=commit_sha,
                branch=branch,
                files_staged=staged_count,
                message=commit_message,
            )

            # Push if configured
            pushed = False
            if self._git_config.mode == "commit-and-push":
                pushed = self._push_to_remote(branch)

            result = CommitResult(
                success=True,
                commit_sha=commit_sha,
                branch=branch,
                files_staged=staged_count,
                pushed=pushed,
                message=commit_message,
                timestamp=timestamp,
            )

            # Audit log
            logger.info(
                "git_commit_audit",
                sha=commit_sha,
                branch=branch,
                feature=feature_name,
                tests_passed=tests_passed,
                duration=duration_seconds,
                pushed=pushed,
                timestamp=timestamp,
            )

            return result

        except GitCommitError:
            raise
        except Exception as e:
            logger.error("git_commit_failed", error=str(e))
            raise GitCommitError(
                operation="commit",
                reason=str(e),
            ) from e

    def _stage_files(self, extra_files: list[str] | None = None) -> int:
        """Stage files matching configured patterns.

        Only stages test-related files: generated test scripts,
        allure results, and any explicitly provided extra files.

        Args:
            extra_files: Additional file paths to stage.

        Returns:
            Number of files staged.
        """
        repo_root = Path(self._repo.working_dir)
        files_to_stage: list[str] = []

        # Expand glob patterns from config
        for pattern in self._git_config.stage_patterns:
            matched = glob.glob(str(repo_root / pattern), recursive=True)
            for filepath in matched:
                # Get path relative to repo root
                rel_path = str(Path(filepath).relative_to(repo_root))
                if rel_path not in files_to_stage:
                    files_to_stage.append(rel_path)

        # Add any extra files
        if extra_files:
            for filepath in extra_files:
                path = Path(filepath)
                if path.is_absolute():
                    rel_path = str(path.relative_to(repo_root))
                else:
                    rel_path = filepath
                if rel_path not in files_to_stage:
                    files_to_stage.append(rel_path)

        # Filter to only existing files with actual changes
        stageable: list[str] = []
        for rel_path in files_to_stage:
            full_path = repo_root / rel_path
            if full_path.exists():
                stageable.append(rel_path)

        if not stageable:
            return 0

        # Stage the files
        try:
            self._repo.index.add(stageable)
            logger.info("git_files_staged", count=len(stageable))
            return len(stageable)
        except Exception as e:
            raise GitCommitError(
                operation="stage",
                reason=f"Failed to stage {len(stageable)} files: {e}",
            ) from e

    def _push_to_remote(self, branch: str) -> bool:
        """Push the commit to the configured remote.

        Args:
            branch: The branch to push.

        Returns:
            True if push succeeded, False otherwise.
        """
        remote_name = self._git_config.remote
        target_branch = self._git_config.branch or branch

        try:
            remote = self._repo.remote(remote_name)
            push_info = remote.push(f"{branch}:{target_branch}")

            # Check push result
            for info in push_info:
                if info.flags & info.ERROR:
                    logger.error(
                        "git_push_failed",
                        remote=remote_name,
                        branch=target_branch,
                        summary=info.summary,
                    )
                    return False

            logger.info(
                "git_push_succeeded",
                remote=remote_name,
                branch=target_branch,
            )
            return True

        except GitCommandError as e:
            logger.error(
                "git_push_error",
                remote=remote_name,
                branch=target_branch,
                error=str(e),
            )
            return False
        except ValueError as e:
            logger.error(
                "git_remote_not_found",
                remote=remote_name,
                error=str(e),
            )
            return False

    def get_recent_test_commits(self, limit: int = 10) -> list[dict]:
        """Retrieve recent test-related commits for audit/reporting.

        Args:
            limit: Maximum number of commits to return.

        Returns:
            List of commit metadata dicts with sha, message, timestamp, author.
        """
        commits: list[dict] = []

        try:
            for commit in self._repo.iter_commits(max_count=limit * 3):
                # Filter to only test commits by our template pattern
                if commit.message.startswith("test("):
                    commits.append({
                        "sha": commit.hexsha,
                        "short_sha": commit.hexsha[:8],
                        "message": commit.message.strip(),
                        "timestamp": commit.committed_datetime.isoformat(),
                        "author": str(commit.author),
                    })
                    if len(commits) >= limit:
                        break
        except Exception as e:
            logger.warning("git_log_retrieval_failed", error=str(e))

        return commits
