# QA Automation & Reporting Agent

AI-powered QA automation agent that generates test scenarios from user stories and site crawling, executes Playwright-based E2E tests, and produces Allure reports — all orchestrated through a LangGraph state machine with Plane.so task board integration.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Option A: Local Development Setup](#option-a-local-development-setup)
  - [Option B: Docker (Full Stack)](#option-b-docker-full-stack)
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

- **RAG-powered test generation** — Ingests user stories (Markdown/JSON), embeds them in ChromaDB, and uses LLM to generate structured test scenarios
- **Site discovery & autonomous test generation** — Crawl any URL with Playwright, extract interactive elements, and auto-generate POM classes + test scripts
- **LangGraph agent orchestration** — State machine with retry logic, conditional routing, and checkpointing
- **Dual LLM provider** — Local Ollama as primary, Google Gemini as fallback (zero-cost development)
- **Plane.so integration** — Auto-creates tasks, listens for webhooks, executes tests when tasks move to DOING
- **Allure reporting** — Rich HTML reports with screenshots on failure, CSV export via API
- **Auto Git commit** — Commits test artifacts on successful runs with structured messages

---

## Prerequisites

| Requirement | Version | Required For |
|-------------|---------|--------------|
| Python | 3.11+ | Core application |
| Docker & Docker Compose | Latest | Full infrastructure stack |
| Ollama | Latest | Local LLM inference (primary) |
| Git | 2.x+ | Auto-commit feature |
| Node.js | 18+ | Only if testing a Node-based target app |

### Installing Ollama (macOS)

```bash
brew install ollama
ollama serve                  # Start the server (runs on port 11434)
ollama pull llama3.2          # Pull the chat model
ollama pull qwen2.5:7b        # Pull the embedding model
```

### Installing Ollama (Linux)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.2
ollama pull qwen2.5:7b
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
python3.11 -m venv .venv
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
docker-compose up -d

# 4. Verify services are running
docker-compose ps
curl http://localhost:8000/health
```

This starts:
- **app** (port 8000) — FastAPI server + LangGraph agent
- **ollama** (port 11434) — Local LLM server
- **allure** (port 5050) — Test report dashboard
- **plane-web** (port 3390) — Task board frontend
- **plane-api** (port 8080) — Task board API
- **plane-db** — PostgreSQL for Plane.so
- **plane-redis** — Redis for Plane.so

### Post-Install: Pull LLM Models

After Ollama is running (locally or in Docker):

```bash
# If running locally
ollama pull llama3.2
ollama pull qwen2.5:7b

# If running in Docker
docker exec qa-agent-ollama ollama pull llama3.2
docker exec qa-agent-ollama ollama pull qwen2.5:7b
```

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
| `LLM_PROVIDER` | `ollama` | Primary LLM: `ollama` or `gemini` |
| **Ollama** | | |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `llama3.2` | Chat/generation model |
| `OLLAMA_EMBEDDING_MODEL` | `qwen2.5:7b` | Embedding model |
| **Google Gemini** | | |
| `GEMINI_API_KEY` | (empty) | Required only if using Gemini |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
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
docker-compose up app
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

## Project Structure

```
agente_testing_automatizado/
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
│   │   ├── routes/          #   Endpoint handlers
│   │   ├── schemas/         #   Pydantic request/response models
│   │   ├── services/        #   Business logic (test_runner, plane_client, git_committer)
│   │   └── middleware/      #   Webhook signature validation
│   └── common/              # Shared utilities
│       ├── logging.py       #   Structured logging (JSON/console)
│       └── exceptions.py    #   Custom exception hierarchy
├── tests/
│   ├── unit/                # 58 fast, isolated tests
│   ├── integration/         # 24 service interaction tests
│   └── e2e/                 # 16 browser-based tests with POM
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
│   ├── Dockerfile           # Main app container
│   ├── Dockerfile.playwright  # Test runner with browsers
│   └── allure/Dockerfile    # Allure report server
├── docker-compose.yml       # Full infrastructure (7 services)
├── pyproject.toml           # Project metadata & tool configuration
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
docker-compose up plane-web plane-api plane-db plane-redis -d

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

### Ollama not connecting

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If in Docker, check container
docker logs qa-agent-ollama

# Pull models if missing
ollama pull llama3.2
ollama pull qwen2.5:7b
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
docker-compose build --no-cache app
docker-compose build --no-cache playwright
```

### Tests failing with "connection refused"

Ensure the target application (`TEST_BASE_URL`) is running and accessible from the test runner's network (use Docker service names if running in Docker).

### Webhook not triggering

1. Check webhook is registered: Plane.so → Workspace Settings → Webhooks
2. Verify secret matches: `PLANE_WEBHOOK_SECRET` in `.env`
3. Check app logs: `docker-compose logs -f app | grep webhook`

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
