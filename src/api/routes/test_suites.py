"""Test Suites API routes.

Provides endpoints for listing, viewing, and running test suites.

Routes:
    GET  /api/test-suites         — List all test suites
    GET  /api/test-suites/{id}    — Get a specific test suite
    POST /api/test-suites/{id}/run — Trigger test execution for a suite
"""

from typing import Any

import aiosqlite
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from src.api.db.connection import get_db
from src.api.middleware.auth_middleware import get_current_user
from src.api.schemas.test_suite import (
    RunSuiteRequest,
    RunSuiteResponse,
    TestSuiteDetailResponse,
    TestSuiteListResponse,
    TestSuiteResponse,
)
from src.api.services.test_suite_service import TestSuiteService
from src.common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/test-suites", tags=["Test Suites"])


@router.post(
    "/scan",
    response_model=TestSuiteListResponse,
    summary="Scan and register test suites",
    description="Scan configured test directories and register discovered test files as suites.",
)
async def scan_test_suites(
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> TestSuiteListResponse:
    """Scan test directories and register new suites.

    Discovers test_*.py files in the configured test directories,
    registers any new ones as suites in the database.
    """
    from pathlib import Path
    import re

    # Configurable directories to scan
    scan_dirs = [
        Path("tests/e2e/generated/tests"),
        Path("tests/e2e"),
    ]

    service = TestSuiteService(db)
    existing_suites, _ = await service.list_suites(limit=1000)
    existing_paths = {s.get("test_path") for s in existing_suites if s.get("test_path")}

    registered = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for test_file in sorted(scan_dir.glob("test_*.py")):
            rel_path = str(test_file)
            if rel_path in existing_paths:
                continue

            # Derive suite name from file
            stem = test_file.stem.replace("test_", "").replace("_", " ").title()
            # Detect category from path
            if "generated" in str(test_file):
                category = "E2E Validation"
            elif "smoke" in test_file.stem:
                category = "Smoke"
            elif "regression" in test_file.stem:
                category = "Regression"
            else:
                category = "E2E Validation"

            suite_data = {
                "name": f"{stem} Tests",
                "category": category,
                "test_path": rel_path,
            }
            new_suite = await service.register_suite(suite_data)
            if new_suite:
                registered.append(new_suite)

    # Return all suites after scan
    all_suites, total = await service.list_suites(limit=100)
    return TestSuiteListResponse(
        data=[TestSuiteResponse(**s) for s in all_suites],
        total=total,
    )


@router.get(
    "",
    response_model=TestSuiteListResponse,
    summary="List test suites",
    description="Retrieve all test suites with optional project, status, and category filters.",
)
async def list_test_suites(
    project_id: str | None = Query(default=None, description="Filter by project ID"),
    suite_status: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status (PENDING, RUNNING, PASSED, FAILED, etc.)",
    ),
    category: str | None = Query(default=None, description="Filter by category"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> TestSuiteListResponse:
    """List all test suites.

    Args:
        project_id: Optional project filter.
        suite_status: Optional status filter.
        category: Optional category filter.
        limit: Max results.
        offset: Pagination offset.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        List of test suites with total count.
    """
    service = TestSuiteService(db)
    suites, total = await service.list_suites(
        project_id=project_id,
        status=suite_status,
        category=category,
        limit=limit,
        offset=offset,
    )

    return TestSuiteListResponse(
        data=[TestSuiteResponse(**s) for s in suites],
        total=total,
    )


@router.get(
    "/{suite_id}",
    response_model=TestSuiteDetailResponse,
    summary="Get test suite",
    description="Get a specific test suite by ID with its steps and status.",
)
async def get_test_suite(
    suite_id: str,
    db: aiosqlite.Connection = Depends(get_db),
    _user: dict[str, Any] = Depends(get_current_user),
) -> TestSuiteDetailResponse:
    """Get a single test suite by ID.

    Args:
        suite_id: The suite identifier.
        db: Database connection.
        _user: Authenticated user.

    Returns:
        Test suite details.

    Raises:
        HTTPException: 404 if suite not found.
    """
    service = TestSuiteService(db)
    suite = await service.get_suite(suite_id)

    if suite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test suite '{suite_id}' not found",
        )

    return TestSuiteDetailResponse(data=TestSuiteResponse(**suite))


@router.post(
    "/{suite_id}/run",
    response_model=RunSuiteResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run test suite",
    description="Trigger test execution for a specific suite. Runs pytest subprocess.",
)
async def run_test_suite(
    suite_id: str,
    body: RunSuiteRequest | None = None,
    db: aiosqlite.Connection = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> RunSuiteResponse:
    """Run a test suite.

    Delegates to the existing TestRunner service for pytest subprocess execution.
    Updates the suite status in the database with results.

    Args:
        suite_id: The suite identifier.
        body: Optional run configuration.
        db: Database connection.
        user: Authenticated user.

    Returns:
        Execution response with updated suite and run details.

    Raises:
        HTTPException: 404 if suite not found.
    """
    if body is None:
        body = RunSuiteRequest()

    service = TestSuiteService(db)

    # Check suite exists
    suite = await service.get_suite(suite_id)
    if suite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test suite '{suite_id}' not found",
        )

    # Check if already running
    if suite.get("status") == "RUNNING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Test suite '{suite_id}' is already running",
        )

    executor = user.get("name", user.get("email", "Unknown"))

    # Execute the suite
    updated_suite, execution_details = await service.run_suite(
        suite_id=suite_id,
        headless=body.headless,
        browser=body.browser,
        tags=body.tags,
        executor=executor,
    )

    if updated_suite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test suite '{suite_id}' not found",
        )

    success = execution_details.get("success", False)
    message = (
        f"Suite execution completed: {execution_details.get('tests_passed', 0)} passed, "
        f"{execution_details.get('tests_failed', 0)} failed"
    )

    return RunSuiteResponse(
        status="success" if success else "error",
        message=message,
        data=TestSuiteResponse(**updated_suite),
        execution=execution_details,
    )
