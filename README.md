# QA Automation & Reporting Agent

AI-powered QA automation agent that generates test scenarios from user stories and site crawling, executes Playwright-based E2E tests, and produces Allure reports — all orchestrated through a LangGraph state machine with Plane.so task board integration.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Option A: Local Development Setup](#option-a-local-development-setup)
  - [Option B: Docker (Full Stack)](#option-b-docker-full-stack)
- [Frontend (TestOps Pro Dashboard)](#frontend-testops-pro-dashboard)
  - [Frontend Setup](#frontend-setup-development)
  - [Frontend Architecture](#frontend-architecture)
  - [Integration with Backend](#how-it-integrates-with-the-qa-agent-backend)
  - [Production Deployment](#production-deployment)
- [Configuration](#configuration)
  - [Environment Variables Reference](#environment-variables-reference)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Seeding User Stories](#seeding-user-stories)
  - [Crawling a Website](#crawling-a-website)
  - [Running Tests](#running-tests)
  - [Viewing Reports](#viewing-reports)
- [Architecture](#architecture)
- [API Reference](#api-reference)
  - [GET /health](#get-health)
  - [POST /crawl](#post-crawl)
  - [POST /webhooks/plane](#post-webhooksplane)
  - [GET /reports/export-csv](#get-reportsexport-csv)
  - [GET /reports/summary](#get-reportssummary)
- [Project Structure](#project-structure)
- [Plane.so Integration](#planeso-integration)
- [Git Auto-Commit](#git-auto-commit)
- [Dashboards](#dashboards)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **TestOps Pro Dashboard** — Full React + TypeScript web UI with Kanban board, test management, analytics charts, user story uploads, and site crawl triggering
- **RAG-powered test generation** — Ingests user stories (Markdown/JSON), embeds them in ChromaDB, and uses LLM to generate structured test scenarios
- **Site discovery & autonomous test generation** — Crawl any URL with Playwright, extract interactive elements, and auto-generate POM classes + test scripts
- **LangGraph agent orchestration** — State machine with retry logic, conditional routing, and checkpointing
- **Dual LLM provider** — Google Gemini as primary (recommended), local Ollama as alternative for offline development
- **Plane.so integration** — Auto-creates tasks, listens for webhooks, executes tests when tasks move to DOING
- **Allure reporting** — Rich HTML reports with screenshots on failure, CSV export via API
- **Auto Git commit** — Commits test artifacts on successful runs with structured messages

---

## Prerequisites

| Requirement | Version | Required For |
|-------------|---------|--------------|
| Python | 3.11+ | Core application |
| Node.js | 18+ | Frontend development and build |
| Docker & Docker Compose | Latest | Full infrastructure stack |
| Git | 2.x+ | Auto-commit feature |
| Gemini API Key | — | LLM inference (recommended) |
| Ollama | Latest | Local LLM inference (optional, offline alternative) |

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create or select a project
3. Generate an API key
4. Add it to your `.env`: `GEMINI_API_KEY=your-key-here`

### Installing Ollama (Optional — for offline/local usage)

```bash
brew install ollama
ollama serve                  # Start the server (runs on port 11434)
ollama pull llama3.2          # Pull the chat model
ollama pull qwen2.5:7b        # Pull the embedding model
```

### Installing Ollama (macOS — optional)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.2
ollama pull qwen2.5:7b
```

### Installing Docker (Linux)
```bash
# Update local packages
sudo apt-get update

# Install Docker Engine and the Compose plugin together
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

## Installation

### Option A: Local Development Setup

Best for contributors and developers who want to run/debug the code directly.

```bash
# 1. Clone the repository
git clone <repository-url>
cd agente_testing_automatizado

# 2. Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows PowerShell

# 3. Install all dependencies (production + dev/test)
pip install -r requirements-dev.txt

# 4. Install Playwright browsers
playwright install chromium
playwright install-deps chromium   # System dependencies (Linux only)

# 5. Configure environment
cp .env.example .env
# Edit .env — see Configuration section below

# 6. Verify installation
python -c "from src.config.settings import get_settings; print(get_settings().app_name)"
# Should print: QA Automation Agent
```

### Option B: Docker (Full Stack)

Best for running the entire system without local Python setup.

```bash
# 1. Clone the repository
git clone <repository-url>
cd agente_testing_automatizado

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Build and start all services
docker compose up -d

# 4. Verify services are running
docker compose ps
curl http://localhost:8000/health
```

This starts:
- **app** (port 8000) — FastAPI server + LangGraph agent + Playwright
- **ollama** (port 11434) — Local LLM server (optional, can be stopped if using Gemini)
- **allure** (port 5050) — Test report dashboard
- **plane-web** (port 3390) — Task board frontend (optional)
- **plane-api** (port 8080) — Task board API (optional)
- **plane-db** — PostgreSQL for Plane.so (optional)
- **plane-redis** — Redis for Plane.so (optional)

> **Tip:** If using Gemini as your LLM provider, you can start only the essential services:
> ```bash
> docker compose up -d app allure
> ```

### Post-Install: Pull LLM Models (only if using Ollama)

If you chose Ollama as your LLM provider:

```bash
# If running locally
ollama pull llama3.2
ollama pull qwen2.5:7b

# If running in Docker
docker exec qa-agent-ollama ollama pull llama3.2
docker exec qa-agent-ollama ollama pull qwen2.5:7b
```

> **Note:** Each model is 2-5GB. If disk space is limited, use `LLM_PROVIDER=gemini` instead.

---

## Frontend (TestOps Pro Dashboard)

The project includes a **TestOps Pro** React + TypeScript frontend (in `frontend/`) that provides a unified web dashboard for the QA Automation Agent. It replaces the need to use CLI tools, curl commands, or third-party dashboards for day-to-day operations.

### What You Can Do from the Frontend

| View | Capabilities |
|------|-------------|
| **Overview Dashboard** | Aggregate test metrics, project health cards, system event feed, live test stream |
| **Kanban Board** | Create, edit, move, and delete test tasks across 6 columns (IDEAS → DONE) |
| **Test Suites** | View registered suites, run them with one click, inspect step-by-step execution logs |
| **Execution Reports** | Charts for daily velocity, failure root causes, pass rate by environment |
| **Projects** | Create and manage test projects with environment and integration settings |
| **User Stories** | Upload stories (MD/JSON), trigger RAG indexing, view which stories have tests |
| **Site Crawl** | Submit a URL, configure crawl depth/pages, view generated POM classes and tests |
| **Settings** | Theme (light/dark), webhook URLs, API credentials, notification preferences |

### Frontend Setup (Development)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start dev server (port 3000, proxies API to backend on port 8000)
npm run dev

# In another terminal, start the backend
cd ..
source .venv/bin/activate
uvicorn src.api.app:app --reload --port 8000
```

Open http://localhost:3000 — the Vite dev server proxies all `/api/*`, `/crawl`, `/health`, and `/webhooks` requests to the backend automatically.

**Default login:** `admin@testops.local` / `admin123`

### Frontend Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server with HMR (port 3000) |
| `npm run build` | TypeScript check + production build to `dist/` |
| `npm run lint` | TypeScript type checking only (`tsc --noEmit`) |
| `npm run preview` | Preview production build locally |
| `npm run clean` | Remove `dist/` directory |

### Frontend Architecture

```
frontend/src/
├── main.tsx                # React entry point
├── App.tsx                 # Root component with providers + view routing
├── index.css              # Tailwind imports + CSS variables (light/dark themes)
├── types.ts               # Shared TypeScript type definitions
├── context/
│   ├── ThemeContext.tsx    # Dark/light mode state
│   ├── AuthContext.tsx     # User session + login/logout (planned)
│   └── AppContext.tsx      # UI state (current view, filters)
├── components/
│   ├── layout/            # Header, Sidebar (navigation shell)
│   ├── dashboard/         # Overview stats, project cards, events feed
│   ├── kanban/            # Kanban board, task cards, task modal
│   ├── tests/             # Test suite list, console inspector
│   ├── reports/           # Recharts analytics (velocity, failures, pass rate)
│   ├── projects/          # Project grid, creation wizard
│   ├── stories/           # User story management + RAG seed trigger
│   ├── crawl/             # Site crawl form + results viewer
│   ├── settings/          # Theme, webhooks, API keys
│   ├── auth/              # Login screen
│   └── shared/            # Badge, Modal, Toast, ErrorBoundary, LoadingSkeleton
├── hooks/                 # Custom React hooks for data fetching + polling
│   └── usePolling.ts      # Generic polling utility hook
├── services/              # Typed API client layer (one file per resource)
│   ├── apiClient.ts       # Base fetch wrapper (handles auth, errors, typing)
│   ├── authService.ts     # POST /api/auth/login, GET /api/auth/me
│   ├── tasksService.ts    # CRUD for /api/tasks
│   ├── projectsService.ts # CRUD for /api/projects
│   ├── testSuitesService.ts # GET/POST /api/test-suites
│   ├── storiesService.ts  # CRUD for /api/stories + seed
│   ├── crawlService.ts    # POST /crawl
│   ├── reportsService.ts  # GET /api/stats/* + /api/reports/analytics
│   └── settingsService.ts # GET/PATCH /api/settings
├── utils/
│   ├── formatters.ts      # Date, duration, number formatters
│   └── constants.ts       # Column definitions, categories, priorities
└── data/
    └── mockData.ts        # Development fallback data (removed in production)
```

### How It Integrates with the QA Agent Backend

The frontend communicates with the FastAPI backend via JSON REST API. All API calls go through the typed `services/apiClient.ts` layer:

```
┌─────────────────────┐         HTTP/JSON          ┌──────────────────────────┐
│  Frontend (React)   │ ──────────────────────────> │  Backend (FastAPI)       │
│  localhost:3000     │  /api/tasks, /api/stories,  │  localhost:8000          │
│                     │  /crawl, /health, etc.      │                          │
│  services/*.ts      │ <────────────────────────── │  routes/*.py             │
└─────────────────────┘      JSON responses         └──────────────────────────┘
         │                                                    │
   Vite proxy (dev)                                    SQLite + ChromaDB
   or static serve (prod)                              + Allure results
```

Key integration points:
- **Auth** → `POST /api/auth/login` returns JWT cookie, all subsequent requests include it
- **Dashboard** → `GET /api/stats/overview` aggregates from SQLite test_suites + events tables
- **Kanban** → `GET/POST/PATCH/DELETE /api/tasks` backed by SQLite, optional Plane.so sync
- **Test Suites** → `POST /api/test-suites/{id}/run` triggers real pytest execution
- **Stories** → `POST /api/stories` persists + triggers RAG indexing in ChromaDB
- **Crawl** → `POST /crawl` (existing endpoint) runs Playwright crawler
- **Reports** → `GET /api/reports/analytics` returns chart data, `/reports/export-csv` returns file

### Production Deployment

In production, the frontend is built and served by FastAPI as static files (single container):

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Set production mode
export ENVIRONMENT=production

# Start server (serves both API and frontend on port 8000)
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Or with Docker (multi-stage build handles everything):

```bash
docker compose up app
# Frontend + API both served on http://localhost:8000
```

### Current Status (Implementation Progress)

The frontend is currently in **Phase 1** (foundation + mock data):
- All views render with mock data from `mockData.ts`
- Components are reorganized into feature-based directories
- API client layer and service modules are scaffolded and typed
- Shared UI components (Modal, Toast, Badge, etc.) are ready
- Vite proxy is configured for seamless backend communication

**Next steps** (per `.kiro/specs/frontend-integration/tasks.md`):
1. Backend: SQLite database layer + new API endpoints
2. Backend: JWT authentication
3. Frontend: Replace mock data with API-backed hooks
4. Frontend: Build Stories and Crawl views (new)
5. Docker: Multi-stage build serving frontend from FastAPI

---

## Configuration

### Environment Variables Reference

Copy `.env.example` to `.env` and customize:

| Variable | Default | Description |
|----------|---------|-------------|
| **Application** | | |
| `ENVIRONMENT` | `development` | `development`, `staging`, or `production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | `console` | `console` (dev) or `json` (prod) |
| `LLM_PROVIDER` | `gemini` | Primary LLM: `gemini` or `ollama` |
| **Ollama (optional)** | | |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `llama3.2` | Chat/generation model |
| `OLLAMA_EMBEDDING_MODEL` | `qwen2.5:7b` | Embedding model |
| **Google Gemini** | | |
| `GEMINI_API_KEY` | (empty) | Required when using Gemini (recommended) |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Gemini model name |
| **Plane.so** | | |
| `PLANE_BASE_URL` | `http://localhost:8080` | Plane.so API URL |
| `PLANE_API_KEY` | (empty) | Your Plane.so API key |
| `PLANE_WORKSPACE_SLUG` | (empty) | Workspace slug |
| `PLANE_PROJECT_ID` | (empty) | Project UUID |
| `PLANE_WEBHOOK_SECRET` | (empty) | Webhook HMAC secret |
| **Test Runner** | | |
| `TEST_BASE_URL` | `http://localhost:3000` | App under test URL |
| `TEST_BROWSER` | `chromium` | `chromium`, `firefox`, `webkit` |
| `TEST_HEADLESS` | `true` | Run browser headlessly |
| **Git Auto-Commit** | | |
| `GIT_ENABLED` | `true` | Enable/disable auto-commit |
| `GIT_MODE` | `commit-only` | `commit-only`, `commit-and-push`, `disabled` |
| `GIT_REMOTE` | `origin` | Git remote name for push |
| **API** | | |
| `API_HOST` | `0.0.0.0` | Server bind address |
| `API_PORT` | `8000` | Server port |

---

## Usage

### Starting the Server

```bash
# Local development (with hot-reload)
uvicorn src.api.app:app --reload --port 8000

# Production
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 2

# Docker
docker compose up app
```

The server is ready when you see: `Uvicorn running on http://0.0.0.0:8000`

### Seeding User Stories

Load sample stories into ChromaDB for the RAG pipeline:

```bash
# Basic usage
python scripts/seed_stories.py

# Custom directory
python scripts/seed_stories.py --stories-dir /path/to/your/stories

# Reset and re-seed
python scripts/seed_stories.py --reset

# Different collection version
python scripts/seed_stories.py --collection user_stories_v2
```

Add your own stories in `data/stories/` using either format:
- **Markdown** (`.md`) — with YAML frontmatter for metadata
- **JSON** (`.json`) — structured array of story objects

### Crawling a Website

Crawl a target site and auto-generate test scripts:

```bash
# Via API
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app.com", "max_depth": 3, "generate_tests": true}'

# Check generated files
ls tests/e2e/generated/pages/    # POM classes
ls tests/e2e/generated/tests/    # Test scripts
```

### Running Tests

Using the convenience script:

```bash
# Make executable (first time)
chmod +x scripts/run_tests.sh

# Available commands
./scripts/run_tests.sh smoke             # Fast critical-path tests
./scripts/run_tests.sh regression        # Full regression suite
./scripts/run_tests.sh e2e              # All E2E browser tests
./scripts/run_tests.sh unit             # Unit tests (no browser)
./scripts/run_tests.sh integration      # Integration tests
./scripts/run_tests.sh all              # Everything
./scripts/run_tests.sh docker-smoke     # Run in Docker container
./scripts/run_tests.sh docker-regression # Regression in Docker
./scripts/run_tests.sh allure-open      # Open Allure report
./scripts/run_tests.sh allure-generate  # Generate static HTML report
./scripts/run_tests.sh clean            # Remove old results
./scripts/run_tests.sh help             # Show all options
```

Or directly with pytest:

```bash
# Unit tests
pytest tests/unit/ -m unit -v

# Smoke tests against a running app
pytest tests/e2e/ -m smoke --base-url=http://localhost:3000

# With Allure output
pytest tests/ --alluredir=./data/allure-results

# Specific browser
pytest tests/e2e/ --browser-name=firefox

# Headed mode (see the browser)
pytest tests/e2e/ --headed
```

### Viewing Reports

```bash
# Option 1: Docker Allure server (always running)
open http://localhost:5050

# Option 2: Local Allure CLI
allure serve ./data/allure-results

# Option 3: Generate static HTML
allure generate ./data/allure-results -o ./data/allure-report --clean
open ./data/allure-report/index.html
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          QA Automation Agent System                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Stories (MD/JSON) ──> RAG System (ChromaDB) ──> LangGraph Agent       │
│  Target URL ──────────────> Site Crawler ───────────> LLM Analysis ──┐      │
│                                                                       │      │
│                              ┌────────────────────────────────────────┘      │
│                              ▼                                               │
│                       Plane.so Task Board                                    │
│                    (TODO → DOING → FINISHED → FAILED)                        │
│                              │ Webhook (status → DOING)                      │
│                              ▼                                               │
│                       FastAPI Core Engine                                     │
│               /health │ /crawl │ /webhooks │ /reports                        │
│                              │                                               │
│                              ▼                                               │
│                    Playwright Test Engine                                     │
│               POM Classes │ Fixtures │ Allure Annotations                    │
│                              │                                               │
│                              ├──> Allure Report Server (HTML dashboard)      │
│                              └──> Git Auto-Commit (on PASS)                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flows

1. **Story → Tests**: User drops `.md`/`.json` → RAG embeds → Agent generates scenarios → Plane.so tasks created
2. **URL → Tests**: POST `/crawl` → Playwright BFS → Element extraction → LLM generates POM + test scripts
3. **Task → Execution**: Plane.so task → DOING → Webhook → pytest subprocess → Allure results → Status update → Git commit

---

## API Reference

### GET /health

System health check with dependency status.

```bash
curl http://localhost:8000/health
```

**Response** (200):
```json
{
  "status": "healthy",
  "timestamp": "2026-07-25T12:00:00+00:00",
  "version": "0.1.0",
  "environment": "development",
  "checks": {
    "chromadb": {"status": "healthy", "collections_count": 1},
    "ollama": {"status": "healthy", "available_models": ["llama3.2", "qwen2.5:7b"]},
    "plane": {"status": "healthy"}
  }
}
```

---

### POST /crawl

Trigger site discovery and optionally generate test scripts.

```bash
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com",
    "max_depth": 3,
    "max_pages": 30,
    "extract_elements": true,
    "screenshot_pages": true,
    "generate_tests": true,
    "headless": true,
    "browser": "chromium"
  }'
```

**Parameters:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | string | (required) | Target URL to crawl |
| `max_depth` | int | 3 | Max navigation depth (1-10) |
| `max_pages` | int | 50 | Max pages to visit (1-200) |
| `extract_elements` | bool | true | Catalog interactive elements |
| `screenshot_pages` | bool | true | Capture screenshots |
| `generate_tests` | bool | true | Auto-generate test scripts |
| `browser` | string | chromium | chromium, firefox, webkit |

**Response** (200):
```json
{
  "status": "completed",
  "start_url": "https://your-app.com",
  "total_pages": 12,
  "max_depth_reached": 2,
  "pages": [
    {"url": "https://your-app.com", "title": "Home", "depth": 0, "elements_count": 15, "links_count": 8, "has_screenshot": true}
  ],
  "suggested_flows": ["Authentication flow: login page → dashboard"],
  "errors": [],
  "test_generation": {
    "pom_files_generated": 5,
    "test_files_generated": 4,
    "total_files": 9,
    "output_directory": "tests/e2e/generated"
  },
  "duration_seconds": 45.2
}
```

---

### POST /webhooks/plane

Receive Plane.so webhook events. When an issue transitions to DOING, triggers test execution.

```bash
curl -X POST http://localhost:8000/webhooks/plane \
  -H "Content-Type: application/json" \
  -H "X-Plane-Signature: <hmac-sha256-hex-signature>" \
  -d '{
    "event": "issue.activity",
    "action": "updated",
    "data": {
      "id": "issue-uuid",
      "name": "[P1] Test Login Flow",
      "state": {"name": "DOING", "group": "started"},
      "priority": "high",
      "labels": [{"id": "lbl-1", "name": "smoke", "color": "#fff"}]
    }
  }'
```

**Response** (200):
```json
{
  "status": "accepted",
  "message": "Test execution triggered for: [P1] Test Login Flow",
  "task_id": "issue-uuid",
  "issue_id": "issue-uuid"
}
```

States that trigger execution: `DOING`, `In Progress`, `started`

---

### GET /reports/export-csv

Download test execution metrics as a CSV file.

```bash
curl -o test_results.csv http://localhost:8000/reports/export-csv
```

**CSV columns:** name, full_name, status, duration_ms, start_time, stop_time, feature, story, severity, suite, description, status_message, duration_seconds, start_datetime, stop_datetime

---

### GET /reports/summary

Get aggregated test results summary.

```bash
curl http://localhost:8000/reports/summary
```

**Response** (200):
```json
{
  "status": "ok",
  "data": {
    "total_tests": 24,
    "passed": 22,
    "failed": 1,
    "broken": 0,
    "skipped": 1,
    "pass_rate": 91.7,
    "total_duration_seconds": 45.3,
    "results_directory": "./data/allure-results",
    "last_updated": "2026-07-25T12:00:00+00:00"
  }
}
```

---

### POST /api/auth/login

Authenticate and receive a session cookie.

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "admin@testops.local", "password": "admin123"}'
```

---

### GET /api/auth/me

Get current authenticated user profile.

```bash
curl http://localhost:8000/api/auth/me -b cookies.txt
```

---

### GET /api/projects

List all projects.

```bash
curl http://localhost:8000/api/projects -b cookies.txt
curl "http://localhost:8000/api/projects?status=ACTIVE" -b cookies.txt
```

---

### POST /api/projects

Create a new project.

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name": "My QA Project", "subtitle": "E2E testing", "environment": "Production"}'
```

---

### GET /api/tasks

List Kanban tasks with optional filters.

```bash
curl "http://localhost:8000/api/tasks" -b cookies.txt
curl "http://localhost:8000/api/tasks?column=IN+PROGRESS&priority=HIGH" -b cookies.txt
```

---

### POST /api/tasks

Create a new task.

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "Write login tests", "category": "Test", "priority": "HIGH", "column_name": "TO DO", "tags": ["smoke"]}'
```

---

### PATCH /api/tasks/{id}/move

Move a task to a different column.

```bash
curl -X PATCH http://localhost:8000/api/tasks/task_abc123/move \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"column_name": "IN PROGRESS"}'
```

---

### GET /api/test-suites

List test suites.

```bash
curl http://localhost:8000/api/test-suites -b cookies.txt
curl "http://localhost:8000/api/test-suites?status=PASSED" -b cookies.txt
```

---

### POST /api/test-suites/{id}/run

Trigger test execution for a suite.

```bash
curl -X POST http://localhost:8000/api/test-suites/suite_abc123/run \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"headless": true, "browser": "chromium"}'
```

---

### GET /api/stories

List user stories.

```bash
curl http://localhost:8000/api/stories -b cookies.txt
curl "http://localhost:8000/api/stories?epic=Authentication&indexed=true" -b cookies.txt
```

---

### POST /api/stories

Create a new user story (triggers RAG indexing).

```bash
curl -X POST http://localhost:8000/api/stories \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "User can reset password", "content": "## Story\nAs a user...", "format": "markdown", "epic": "Auth", "feature": "Password Reset"}'
```

---

### POST /api/stories/seed

Seed all unindexed stories into ChromaDB.

```bash
curl -X POST http://localhost:8000/api/stories/seed \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"reset": false}'
```

---

### GET /api/stats/overview

Dashboard overview metrics.

```bash
curl http://localhost:8000/api/stats/overview -b cookies.txt
```

---

### GET /api/stats/velocity

Daily test velocity (pass/fail counts per day).

```bash
curl "http://localhost:8000/api/stats/velocity?days=30" -b cookies.txt
```

---

### GET /api/stats/failures

Failure breakdown by category.

```bash
curl http://localhost:8000/api/stats/failures -b cookies.txt
```

---

### GET /api/reports/analytics

Combined analytics data for charts.

```bash
curl "http://localhost:8000/api/reports/analytics?days=14" -b cookies.txt
```

---

### GET /api/settings

Get all application settings.

```bash
curl http://localhost:8000/api/settings -b cookies.txt
```

---

### PATCH /api/settings

Update application settings.

```bash
curl -X PATCH http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"settings": {"theme": "dark", "notifications_enabled": "true"}}'
```

---

## Project Structure

```
agente_testing_automatizado/
├── frontend/                # TestOps Pro React dashboard
│   ├── src/
│   │   ├── components/      # Feature-based UI components
│   │   ├── context/         # React Context providers
│   │   ├── hooks/           # Data-fetching custom hooks
│   │   ├── services/        # Typed API client layer
│   │   ├── utils/           # Formatters, constants
│   │   ├── App.tsx          # Root component
│   │   └── types.ts         # Shared TypeScript types
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.ts       # Vite + API proxy configuration
│   └── tsconfig.json        # TypeScript strict config
├── src/
│   ├── config/              # Pydantic settings, environment configuration
│   │   └── settings.py      #   All app settings with env var loading
│   ├── rag/                 # RAG (Retrieval-Augmented Generation)
│   │   ├── loader.py        #   Markdown & JSON document loaders
│   │   ├── splitter.py      #   Semantic text chunking
│   │   ├── embeddings.py    #   Ollama/Gemini embedding abstraction
│   │   ├── vectorstore.py   #   ChromaDB persistent storage
│   │   └── retriever.py     #   Similarity search service
│   ├── agent/               # LangGraph state machine
│   │   ├── state.py         #   AgentState TypedDict + Pydantic models
│   │   ├── graph.py         #   Graph definition with conditional edges
│   │   ├── llm_provider.py  #   LLM abstraction with fallback + retry
│   │   ├── nodes/           #   Processing nodes (ingest, generate, prioritize, publish)
│   │   └── prompts/         #   Prompt templates with few-shot examples
│   ├── crawler/             # Site discovery engine
│   │   ├── engine.py        #   Playwright BFS crawler
│   │   ├── config.py        #   CrawlConfig dataclass
│   │   ├── element_extractor.py  # DOM element cataloging
│   │   ├── sitemap_builder.py    # Site map + report generation
│   │   └── test_generator.py     # POM + test script generation
│   ├── api/                 # FastAPI application
│   │   ├── app.py           #   App factory with middleware
│   │   ├── routes/          #   Endpoint handlers (existing + new /api/* for frontend)
│   │   ├── schemas/         #   Pydantic request/response models
│   │   ├── services/        #   Business logic (test_runner, plane_client, git_committer)
│   │   ├── middleware/      #   Webhook signature validation, JWT auth
│   │   └── db/              #   SQLite connection, migrations, repositories (planned)
│   └── common/              # Shared utilities
│       ├── logging.py       #   Structured logging (JSON/console)
│       └── exceptions.py    #   Custom exception hierarchy
├── tests/
│   ├── unit/                # Fast, isolated tests
│   ├── integration/         # Service interaction tests
│   └── e2e/                 # Browser-based tests with POM
│       ├── pages/           #   Page Object Model classes
│       ├── generated/       #   Auto-generated tests from crawl
│       ├── test_smoke.py    #   Quick validation suite
│       └── test_regression.py  # Full regression suite
├── data/
│   ├── stories/             # User story input documents
│   ├── chroma/              # ChromaDB persistent vector storage
│   └── allure-results/      # Test execution results
├── scripts/
│   ├── setup_plane.sh       # Plane.so provisioning & webhook setup
│   ├── seed_stories.py      # Load stories into ChromaDB
│   └── run_tests.sh         # CLI test runner helper
├── docker/
│   ├── Dockerfile           # Main app container (+ frontend in production)
│   ├── Dockerfile.playwright  # Test runner with browsers
│   └── allure/Dockerfile    # Allure report server
├── docker-compose.yml       # Full infrastructure (7+ services)
├── .kiro/
│   ├── specs/               # Feature specifications (Kiro SDD format)
│   │   ├── qa-automation-agent/   # Backend agent spec
│   │   └── frontend-integration/  # Frontend integration spec
│   └── steering/            # Coding standards and guidelines
├── pyproject.toml           # Python project metadata
├── requirements.txt         # Production dependencies (pinned)
├── requirements-dev.txt     # Development/test dependencies
├── pytest.ini               # Pytest markers & options
├── .env.example             # Environment variable template
└── .gitignore               # Git exclusions
```

---

## Plane.so Integration

### Automated Setup

```bash
# 1. Start Plane.so services
docker compose up plane-web plane-api plane-db plane-redis -d

# 2. Wait for startup (30-60 seconds)
sleep 30

# 3. Run provisioning script
source .env && ./scripts/setup_plane.sh

# 4. Copy the output values to your .env file
```

### Manual Webhook Registration

If the automated script can't register the webhook:

1. Open Plane.so at http://localhost:3390
2. Go to **Workspace Settings** → **Webhooks**
3. Click **Add Webhook**
4. Set URL: `http://app:8000/webhooks/plane` (Docker) or `http://localhost:8000/webhooks/plane` (local)
5. Enable events: **Issues** (state changes)
6. Copy the generated secret
7. Add to `.env`: `PLANE_WEBHOOK_SECRET=<your-secret>`

### Workflow

1. Agent creates tasks in Plane.so with generated test scenarios
2. QA engineer or automation moves a task to **DOING**
3. Webhook fires → FastAPI receives → pytest runs matching tests
4. On success: task → **FINISHED**, git commit created
5. On failure: task → **FAILED**, screenshot attached

---

## Git Auto-Commit

When all tests in a feature pass, the agent automatically commits test artifacts:

```
test(login-flow): PASSED - 2026-07-25 12:00:00 UTC - 12 tests passed in 45.2s
```

### Configuration

| Variable | Options | Description |
|----------|---------|-------------|
| `GIT_MODE` | `commit-only` | Create local commit (default) |
| | `commit-and-push` | Commit and push to remote |
| | `disabled` | No git operations |
| `GIT_REMOTE` | `origin` | Remote name for push |
| `GIT_BRANCH` | (empty) | Target branch (empty = current) |
| `GIT_STAGE_PATTERNS` | `tests/e2e/generated/**,data/allure-results/**` | Files to stage |

### What Gets Committed

- Generated test scripts (`tests/e2e/generated/`)
- Allure result files (`data/allure-results/`)
- Any additional files matching configured patterns

---

## Dashboards

| Service | URL | Description |
|---------|-----|-------------|
| FastAPI Docs | http://localhost:8000/docs | Interactive OpenAPI documentation |
| FastAPI ReDoc | http://localhost:8000/redoc | Alternative API docs |
| Allure Reports | http://localhost:5050 | Test execution dashboards |
| Plane.so Board | http://localhost:3390 | QA task management |
| Ollama API | http://localhost:11434 | LLM model management |

---

## Troubleshooting

### ChromaDB telemetry errors in logs

If you see repeated `Failed to send telemetry event ClientStartEvent` errors:

```bash
# Add to .env to silence telemetry
ANONYMIZED_TELEMETRY=false
```

Then restart: `docker compose restart app`

### Ollama not connecting (only if using LLM_PROVIDER=ollama)

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If in Docker, check container
docker logs qa-agent-ollama

# Pull models if missing
ollama pull llama3.2
ollama pull qwen2.5:7b

# Alternative: switch to Gemini to avoid local model issues
# Set LLM_PROVIDER=gemini in .env and restart
```

### ChromaDB errors on startup

```bash
# Reset the vector store
rm -rf data/chroma/*
python scripts/seed_stories.py --reset
```

### Playwright browser not found

```bash
# Reinstall browsers
playwright install chromium
playwright install-deps chromium  # Linux system deps
```

### Docker build failures

```bash
# Rebuild without cache
docker compose build --no-cache app
docker compose build --no-cache playwright
```

### Tests failing with "connection refused"

Ensure the target application (`TEST_BASE_URL`) is running and accessible from the test runner's network (use Docker service names if running in Docker).

### Webhook not triggering

1. Check webhook is registered: Plane.so → Workspace Settings → Webhooks
2. Verify secret matches: `PLANE_WEBHOOK_SECRET` in `.env`
3. Check app logs: `docker compose logs -f app | grep webhook`

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes following the existing code patterns
4. Add tests for new functionality
5. Run the test suite: `./scripts/run_tests.sh all`
6. Commit with conventional format: `feat(module): description`
7. Open a Pull Request

---

## License

MIT
