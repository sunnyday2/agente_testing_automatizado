"""Allure test results collector.

Manages Allure result files: collects them from test runs, provides
summary statistics for reporting, and exports data for CSV download.

Usage:
    from src.api.services.allure_collector import AllureCollector

    collector = AllureCollector()
    summary = collector.get_latest_summary()
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


class AllureCollector:
    """Manages Allure test result artifacts."""

    def __init__(self, results_dir: str | None = None) -> None:
        settings = get_settings()
        self._results_dir = Path(results_dir or settings.test_runner.allure_results_dir)
        self._results_dir.mkdir(parents=True, exist_ok=True)

    @property
    def results_dir(self) -> Path:
        return self._results_dir

    def collect_results(self, source_dir: str | Path) -> int:
        """Copy Allure result files from source to the results directory.

        Returns number of files collected.
        """
        source = Path(source_dir)
        if not source.exists():
            logger.warning("allure_source_dir_not_found", path=str(source))
            return 0

        collected = 0
        valid_suffixes = {".json", ".xml", ".txt", ".png", ".attach"}
        for file_path in source.iterdir():
            if file_path.is_file() and file_path.suffix in valid_suffixes:
                dest = self._results_dir / file_path.name
                shutil.copy2(str(file_path), str(dest))
                collected += 1

        logger.info("allure_results_collected", count=collected, source=str(source))
        return collected

    def get_latest_summary(self) -> dict:
        """Parse result files and return pass/fail/skip summary."""
        results = self._parse_result_files()

        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        broken = sum(1 for r in results if r.get("status") == "broken")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        total_duration_ms = sum(r.get("time", {}).get("duration", 0) for r in results)

        return {
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "broken": broken,
            "skipped": skipped,
            "pass_rate": round(passed / max(len(results), 1) * 100, 1),
            "total_duration_seconds": round(total_duration_ms / 1000, 2),
            "results_directory": str(self._results_dir),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    def get_results_for_export(self) -> list[dict]:
        """Get detailed results suitable for CSV export."""
        results = self._parse_result_files()
        export_rows: list[dict] = []

        for result in results:
            time_info = result.get("time", {})
            labels = {
                label.get("name", ""): label.get("value", "")
                for label in result.get("labels", [])
            }
            export_rows.append({
                "name": result.get("name", "Unknown"),
                "full_name": result.get("fullName", ""),
                "status": result.get("status", "unknown"),
                "duration_ms": time_info.get("duration", 0),
                "start_time": time_info.get("start", 0),
                "stop_time": time_info.get("stop", 0),
                "feature": labels.get("feature", ""),
                "story": labels.get("story", ""),
                "severity": labels.get("severity", ""),
                "suite": labels.get("suite", ""),
                "description": result.get("description", ""),
                "status_message": result.get("statusDetails", {}).get("message", ""),
            })

        return export_rows

    def clean_old_results(self, max_age_days: int = 7) -> int:
        """Remove result files older than max_age_days. Returns count removed."""
        cutoff = datetime.now(timezone.utc).timestamp() - (max_age_days * 86400)
        removed = 0

        for file_path in self._results_dir.iterdir():
            if file_path.is_file() and file_path.name != ".gitkeep":
                if file_path.stat().st_mtime < cutoff:
                    file_path.unlink()
                    removed += 1

        if removed:
            logger.info("allure_old_results_cleaned", removed=removed)
        return removed

    def _parse_result_files(self) -> list[dict]:
        """Parse all Allure *-result.json files."""
        results: list[dict] = []
        for file_path in self._results_dir.glob("*-result.json"):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                results.append(data)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("allure_result_parse_failed", file=str(file_path), error=str(e))
        return results
