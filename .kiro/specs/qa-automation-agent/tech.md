# Technical Design: QA Automation & Reporting Agent

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          QA Automation Agent System                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────────────────┐ │
│  │  User Story  │───>│   RAG System     │───>│   LangGraph Agent         │ │
│  │  Documents   │    │  (ChromaDB +     │    │  (Decision + Generation)  │ │
│  │  (MD/JSON)   │    │   Embeddings)    │    │                           │ │
│  └──────────────┘    └──────────────────┘    └─────────────┬─────────────┘ │
│                                                            │               │
│  ┌──────────────┐                                          │               │
│  │  Target URL  │───> Site Crawler ───> LLM Analysis ──────┤               │
│  └──────────────┘                                          │               │
│                                                            ▼               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Plane.so Task Board                           │  │
│  │              TODO  │  DOING  │  FINISHED  │  FAILED                  │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │ Webhook (status -> DOING)                 │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI Core Engine                               │  │
│  │  /webhooks/plane  │  /crawl  │  /reports/export-csv  │  /health      │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   Playwright Test Engine                              │  │
│  │  POM Classes  │  Conftest  │  Fixtures  │  Allure Annotations        │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Allure Report Server (Docker)                            │  │
│  │              CSV Export  │  Web Dashboard                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology Decisions

### TD-1: Python 3.11+ as Core Language
**Decision:** Use Python 3.11+ for the entire system.
**Rationale:**
- Native async support via asyncio for concurrent test execution
- Rich ecosystem for AI/ML (LangChain, LangGraph)
- First-class Playwright support via playwright-python
- FastAPI leverages Python type hints for validation and documentation

### TD-2: LangChain + ChromaDB for RAG
**Decision:** Use LangChain document loaders with ChromaDB vector store.
**Rationale:**
- LangChain provides battle-tested document loaders for Markdown/JSON
- ChromaDB offers lightweight persistent vector storage (no external DB server)
- RecursiveCharacterTextSplitter preserves semantic boundaries in user stories
- Embedding flexibility: switch between Ollama local and Google cloud embeddings

**Configuration:**
- Chunk size: 500 tokens, overlap: 50 tokens
- Similarity search top_k: 3
- Embedding model: `qwen2.5:7b` (local) / `models/embedding-001` (Google)
- Persistent storage: `./data/chroma`

### TD-3: LangGraph for Agent Orchestration
**Decision:** Use LangGraph state machine for agent decision flow.
**Rationale:**
- Explicit state management via TypedDict avoids implicit side-effects
- Conditional edges enable retry/fallback patterns
- Built-in support for checkpointing and resumability
- Clear separation between decision nodes (LLM calls) and action nodes (API calls)

**State Schema:**
```python
class AgentState(TypedDict):
    user_story_text: str
    retrieved_docs: list[Document]
    test_scenarios: list[TestScenario]
    site_map: Optional[SiteMap]
    plane_task_id: Optional[str]
    execution_status: Literal["pending", "running", "passed", "failed"]
    crawl_results: Optional[CrawlResults]
```

### TD-4: Dual LLM Provider Strategy
**Decision:** Local Ollama as primary, Google Gemini API as fallback.
**Rationale:**
- Zero-cost development/testing with local models
- No data leaves the network during normal operation
- Cloud fallback ensures availability during local GPU constraints
- Abstraction layer enables transparent switching

**Models:**
- Local: `llama3.2` or `qwen2.5:7b` via Ollama
- Cloud: `gemini-2.5-flash` via Google Generative AI API

### TD-5: FastAPI as Core Engine
**Decision:** Use FastAPI + Uvicorn for the API and webhook layer.
**Rationale:**
- Native async handlers for non-blocking webhook processing
- Pydantic models enforce strict request/response validation
- Background tasks for fire-and-forget test execution
- Auto-generated OpenAPI docs for integration testing

**Endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/webhooks/plane` | Receive Plane.so task status changes |
| POST | `/crawl` | Trigger site discovery from URL |
| POST | `/generate-tests` | Generate tests from user stories or crawl results |
| GET | `/reports/export-csv` | Download test metrics as CSV |
| PATCH | `/tasks/{id}/status` | Update task status callback |
| GET | `/health` | System health check |

### TD-6: Playwright with Page Object Model
**Decision:** Use pytest-playwright with POM pattern and Allure integration.
**Rationale:**
- Cross-browser support (Chromium, Firefox, WebKit) out of the box
- POM provides maintainable, reusable test components
- pytest fixtures handle browser lifecycle and parallelization
- allure-pytest provides rich annotations and failure screenshots

### TD-7: Site Crawler Architecture
**Decision:** Custom Playwright-based crawler with LLM analysis layer.
**Rationale:**
- Playwright provides real browser rendering (handles SPAs, dynamic content)
- LLM analyzes DOM structure to identify meaningful user flows
- Depth-limited BFS traversal prevents infinite loops
- Element cataloging builds a structured site map for test generation

**Crawler Configuration:**
```python
@dataclass
class CrawlConfig:
    max_depth: int = 3
    max_pages: int = 50
    timeout_per_page: int = 10000  # ms
    exclude_patterns: list[str] = field(default_factory=lambda: [
        r".*\.(pdf|zip|png|jpg|gif)$",
        r".*logout.*",
        r".*#.*"
    ])
    extract_elements: bool = True
    screenshot_pages: bool = True
```

### TD-8: Docker Compose Infrastructure
**Decision:** Multi-container Docker Compose for all services.
**Rationale:**
- Single `docker-compose up` brings up entire system
- Service isolation with shared networking
- Volume mounts for persistent data (ChromaDB, Allure results)
- Non-technical users access dashboards without local tooling

**Services:**
- `app` - FastAPI core engine + LangGraph agent
- `plane-web` - Plane.so frontend
- `plane-api` - Plane.so backend
- `plane-db` - PostgreSQL for Plane.so
- `plane-redis` - Redis for Plane.so
- `allure` - Allure Report Server
- `chromadb` - ChromaDB vector store (optional, can be embedded)

### TD-9: Automatic Git Commit on Test Success
**Decision:** Use GitPython library for programmatic Git operations after successful test runs.
**Rationale:**
- Provides traceability: each successful test run is tracked in version history
- Enables audit trail of test coverage evolution over time
- Supports CI/CD pipelines by keeping test artifacts in sync with code changes
- Configurable behavior allows teams to choose commit-only or commit-and-push

**Implementation:**
```python
@dataclass
class GitCommitConfig:
    enabled: bool = True
    mode: Literal["commit-only", "commit-and-push", "disabled"] = "commit-only"
    remote: str = "origin"
    branch: Optional[str] = None  # None = current branch
    stage_patterns: list[str] = field(default_factory=lambda: [
        "tests/e2e/generated/**",
        "data/allure-results/**",
    ])
    commit_message_template: str = "test({feature}): PASSED - {timestamp} - {summary}"
```

**Commit Flow:**
1. Test runner completes with exit code 0 (all tests passed)
2. Git service stages files matching configured patterns
3. Commit created with structured message including feature name, timestamp, test count
4. If mode is "commit-and-push": push to remote branch
5. Log commit SHA and metadata for audit

## Data Flow

### Flow 1: User Story → Test Generation
```
1. User drops .md/.json into /data/stories/
2. RAG loader parses, chunks, embeds → ChromaDB
3. LangGraph agent retrieves relevant context
4. LLM generates test scenarios with priorities
5. Agent creates Plane.so tasks via API
```

### Flow 2: URL → Site Discovery → Test Generation
```
1. User submits URL via POST /crawl
2. Playwright crawler navigates site (BFS, depth-limited)
3. Per page: extract elements, capture screenshot, catalog actions
4. LLM analyzes site map → generates test scenarios
5. System produces POM classes + test scripts
6. Tests stored in /tests/generated/
```

### Flow 3: Task Execution → Reporting → Git Commit
```
1. Plane.so task moved to DOING (manually or automatically)
2. Webhook fires → FastAPI receives event
3. Background task launches Playwright pytest subprocess
4. Results written to /allure-results volume
5. Allure server picks up results → renders HTML report
6. FastAPI patches task status back to Plane.so (FINISHED/FAILED)
7. If FINISHED: Git service stages test artifacts and commits
8. If commit-and-push mode: push to configured remote branch
```

## Security Considerations
- Plane.so API keys stored in environment variables (never in code)
- Webhook endpoint validates request signatures
- Crawl depth limits prevent abuse of the site discovery feature
- URL allowlist/blocklist configurable for crawl targets
- No user data persisted beyond test execution metadata

## Error Handling Strategy
- **LLM failures:** Automatic fallback Ollama → Gemini with exponential backoff
- **Crawler errors:** Skip failed pages, continue crawl, log errors
- **Test failures:** Capture screenshot + trace, mark task as FAILED
- **Webhook failures:** Return 200 immediately, process async, retry on failure
- **ChromaDB failures:** Graceful degradation, direct LLM call without RAG context
