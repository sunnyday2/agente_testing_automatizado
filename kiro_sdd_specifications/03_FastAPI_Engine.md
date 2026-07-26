# Feature 3 Specification: FastAPI Core Engine & Webhook Handler

## 1. System Overview
The FastAPI Core Engine acts as the orchestrator between Plane.so, Playwright execution, CSV data export, and Allure reporting.

## 2. Technical Stack
- **Framework:** `fastapi`, `uvicorn`, `pydantic`
- **Data Processing:** `pandas`
- **Process Execution:** `asyncio.create_subprocess_exec`

## 3. Tasks Breakdown (Max 6 Tasks)

### [API-01] FastAPI Project Setup
- Initialize FastAPI app, middleware, background task pools, and standard JSON response schemas.

### [API-02] Plane.so Webhook Endpoint
- Create POST `/webhooks/plane` listener filtering for status transitions to `DOING`.

### [API-03] Asynchronous Test Runner Service
- Background task executor launching Playwright CLI processes asynchronously upon webhook calls.

### [API-04] Allure Report Collector
- Hook to move execution logs/results into the shared Allure results volume (`/allure-results`).

### [API-05] CSV Data Export Endpoint
- GET `/reports/export-csv` transforming test execution metrics into downloadable CSV files via Pandas.

### [API-06] Status Callback Handler
- Patch request back to Plane.so API setting task state to `FINISHED` or `FAILED` based on exit codes.