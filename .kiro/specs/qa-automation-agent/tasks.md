# Implementation Tasks: QA Automation & Reporting Agent

## Phase 1: Project Foundation

### Task 1: Project Scaffolding & Configuration
- [ ] Create directory structure as defined in structure.md
- [ ] Set up `pyproject.toml` with project metadata and dependencies
- [ ] Create `requirements.txt` (production) and `requirements-dev.txt` (dev/test)
- [ ] Implement `src/config/settings.py` with Pydantic BaseSettings
- [ ] Create `.env.example` with all required environment variables
- [ ] Set up `.gitignore` for Python, data directories, and env files
- [ ] Configure `pytest.ini` with markers and default options

### Task 2: Common Utilities & Logging
- [ ] Implement `src/common/logging.py` with structured JSON logging
- [ ] Implement `src/common/exceptions.py` with custom exception hierarchy
- [ ] Set up logging configuration for different environments (dev/prod)

## Phase 2: RAG System

### Task 3: Document Loader & Splitter
- [ ] Implement `src/rag/loader.py` with Markdown and JSON document loaders
- [ ] Implement `src/rag/splitter.py` with RecursiveCharacterTextSplitter (chunk_size=500, overlap=50)
- [ ] Add metadata extraction (epic, feature, target_role) during loading
- [ ] Create sample user story documents in `data/stories/`

### Task 4: Vector Store & Retriever
- [ ] Implement `src/rag/embeddings.py` with Ollama/Google embedding abstraction
- [ ] Implement `src/rag/vectorstore.py` with ChromaDB persistent client setup
- [ ] Implement `src/rag/retriever.py` with StoryRetriever service (top_k=3, threshold)
- [ ] Add collection versioning support (`user_stories_v1`)

## Phase 3: LangGraph Agent

### Task 5: Agent State & LLM Provider
- [ ] Implement `src/agent/state.py` with AgentState TypedDict
- [ ] Implement `src/agent/llm_provider.py` with Ollama/Gemini abstraction and fallback
- [ ] Add retry logic with exponential backoff (max 3 attempts)
- [ ] Implement structured output parsing using Pydantic models (TestScenario)

### Task 6: Agent Nodes & Prompts
- [ ] Implement `src/agent/prompts/test_generation.py` with few-shot examples
- [ ] Implement `src/agent/prompts/priority_assignment.py`
- [ ] Implement `src/agent/prompts/site_analysis.py` for URL-based analysis
- [ ] Implement `src/agent/nodes/ingest.py` — story ingestion node
- [ ] Implement `src/agent/nodes/generate.py` — test scenario generation node
- [ ] Implement `src/agent/nodes/prioritize.py` — priority assignment node
- [ ] Implement `src/agent/nodes/publish.py` — Plane.so task creation node

### Task 7: LangGraph Graph Definition
- [ ] Implement `src/agent/graph.py` with full state machine
- [ ] Define conditional edges (route after generation, retry logic)
- [ ] Add checkpointing before each node for recovery
- [ ] Wire up all nodes with proper state transitions

## Phase 4: Site Crawler

### Task 8: Crawler Engine
- [ ] Implement `src/crawler/config.py` with CrawlConfig dataclass
- [ ] Implement `src/crawler/engine.py` with Playwright BFS crawler
- [ ] Add URL normalization and deduplication
- [ ] Implement depth limiting and max pages constraint
- [ ] Add robots.txt respect and exclude pattern filtering

### Task 9: Element Extraction & Site Map
- [ ] Implement `src/crawler/element_extractor.py` — DOM element cataloging
- [ ] Implement `src/crawler/sitemap_builder.py` — PageNode/SiteMap construction
- [ ] Add screenshot capture per page
- [ ] Implement site map summary report generation

### Task 10: Test Generation from Crawl
- [ ] Implement `src/crawler/test_generator.py` — LLM-based test generation
- [ ] Generate POM classes from discovered page elements
- [ ] Generate test scripts grouped by user flow
- [ ] Write generated files to `tests/e2e/generated/` with metadata headers

## Phase 5: FastAPI Core Engine

### Task 11: FastAPI Application Setup
- [ ] Implement `src/api/app.py` with factory pattern, middleware, CORS
- [ ] Implement `src/api/routes/health.py` with dependency health checks
- [ ] Implement `src/api/middleware/webhook_validator.py` for signature verification
- [ ] Define common response schemas in `src/api/schemas/`

### Task 12: Webhook & Crawl Endpoints
- [ ] Implement `src/api/schemas/webhook.py` with Plane.so payload models
- [ ] Implement `src/api/routes/webhooks.py` — POST /webhooks/plane
- [ ] Implement `src/api/schemas/crawl.py` with crawl request/response models
- [ ] Implement `src/api/routes/crawl.py` — POST /crawl (trigger site discovery)

### Task 13: Services & Reporting
- [ ] Implement `src/api/services/test_runner.py` — async subprocess launcher
- [ ] Implement `src/api/services/plane_client.py` — Plane.so API client (create task, update status)
- [ ] Implement `src/api/services/allure_collector.py` — results file mover
- [ ] Implement `src/api/services/git_committer.py` — auto Git commit on successful test execution
- [ ] Implement `src/api/routes/reports.py` — GET /reports/export-csv with Pandas

### Task 13.1: Git Commit Service
- [ ] Implement `GitCommitConfig` dataclass with mode (commit-only, commit-and-push, disabled)
- [ ] Implement git staging logic using GitPython (stage only test artifacts matching patterns)
- [ ] Implement structured commit message formatting: `test(feature): PASSED - timestamp - summary`
- [ ] Implement optional push-to-remote with branch configuration
- [ ] Add commit SHA and metadata logging for audit trail
- [ ] Add guard: only commit when all tests in the feature pass (exit code 0)
- [ ] Wire git_committer into the test_runner flow (called after FINISHED status)

## Phase 6: Playwright Test Suite

### Task 14: Test Framework Setup
- [ ] Create `tests/e2e/conftest.py` with browser fixtures and base URL config
- [ ] Implement `tests/e2e/pages/base_page.py` with common POM utilities
- [ ] Add Allure failure screenshot fixture (autouse)
- [ ] Configure headless mode and browser selection

### Task 15: Page Objects & Sample Tests
- [ ] Implement sample POM classes (login, dashboard, navigation)
- [ ] Create `tests/e2e/test_smoke.py` with basic smoke tests
- [ ] Create `tests/e2e/test_regression.py` skeleton with markers
- [ ] Verify Allure annotation patterns work end-to-end

## Phase 7: Infrastructure

### Task 16: Docker Configuration
- [ ] Create `docker/Dockerfile` for main application
- [ ] Create `docker/Dockerfile.playwright` with browsers pre-installed
- [ ] Create `docker/allure/Dockerfile` if customization needed
- [ ] Create `docker-compose.yml` with all services, networks, volumes

### Task 17: Plane.so & Allure Setup
- [ ] Create `scripts/setup_plane.sh` for initial Plane.so provisioning
- [ ] Create `scripts/seed_stories.py` for loading sample data into ChromaDB
- [ ] Create `scripts/run_tests.sh` as CLI helper
- [ ] Document webhook registration steps in Plane.so

## Phase 8: Integration & Validation

### Task 18: Unit Tests
- [ ] Write unit tests for RAG loader and retriever
- [ ] Write unit tests for agent state and LLM provider
- [ ] Write unit tests for crawler engine (mock Playwright)
- [ ] Write unit tests for API schemas and services

### Task 19: Integration Tests
- [ ] Write integration test for webhook → test runner flow
- [ ] Write integration test for crawl → test generation flow
- [ ] Write integration test for full agent pipeline (story → task)
- [ ] Verify end-to-end docker-compose setup starts cleanly

### Task 20: Documentation & Final Validation
- [ ] Update README.md with full setup instructions
- [ ] Document API endpoints with curl examples
- [ ] Verify all success metrics from product.md are measurable
- [ ] Run full smoke suite and generate first Allure report
