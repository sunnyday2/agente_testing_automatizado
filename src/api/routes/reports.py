"""Reports endpoint for exporting test metrics.

Provides CSV export of test execution results from Allure data
and a JSON summary endpoint.

Endpoints:
    GET /reports/export-csv
    GET /reports/summary
"""

import io
from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.api.services.allure_collector import AllureCollector
from src.common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/reports/export-csv")
async def export_csv() -> StreamingResponse:
    """Export test execution metrics as a downloadable CSV file.

    Reads Allure result files and returns a CSV with test name, status,
    duration, feature, story, and severity columns.
    """
    logger.info("csv_export_requested")

    collector = AllureCollector()
    results = collector.get_results_for_export()

    if not results:
        # Empty CSV with correct headers
        columns = [
            "name", "full_name", "status", "duration_ms", "start_time",
            "stop_time", "feature", "story", "severity", "suite",
            "description", "status_message",
        ]
        df = pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(results)
        df["duration_seconds"] = df["duration_ms"] / 1000.0
        df["start_datetime"] = pd.to_datetime(
            df["start_time"], unit="ms", utc=True, errors="coerce"
        )
        df["stop_datetime"] = pd.to_datetime(
            df["stop_time"], unit="ms", utc=True, errors="coerce"
        )

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.csv"

    logger.info("csv_export_generated", rows=len(df), filename=filename)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/reports/summary")
async def get_summary() -> dict:
    """Get a JSON summary of the latest test execution results.

    Returns pass/fail/skip counts, pass rate, and timing.
    """
    collector = AllureCollector()
    summary = collector.get_latest_summary()
    return {"status": "ok", "data": summary}
