# Project Structure: QA Automation & Reporting Agent

## Root Directory Layout

```
agente_testing_automatizado/
├── .kiro/
│   ├── specs/
│   │   └── qa-automation-agent/
│   │       ├── product.md
│   │       ├── tech.md
│   │       ├── structure.md
│   │       └── tasks.md
│   └── steering/
│       ├── coding-standards.md
│       ├── testing-standards.md
│       ├── agent-architecture.md
│       └── infrastructure.md
├── kiro_sdd_specifications/          # Original architecture reference docs
│   ├── 00_README.md
│   ├── 01_RAG_System.md
│   ├── 02_LangGraph_Agent.md
│   ├── 03_FastAPI_Engine.md
│   ├── 04_Playwright_Tests.md
│   └── 05_Infrastructure.md
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py               # Pydantic BaseSettings, env vars
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── loader.py                  # Document loaders (MD, JSON)
│   │   ├── splitter.py                # Text chunking logic
│   │   ├── embeddings.py             # Embedding provider abstraction
│   │   ├── vectorstore.py            # ChromaDB initialization & queries
│   │   └── retriever.py              # StoryRetriever service
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── state.py                   # AgentState TypedDict
│   │   ├── graph.py                   # LangGraph graph definition
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py             # Story ingestion node
│   │   │   ├── generate.py           # Test scenario generation node
│   │   │   ├── prioritize.py         # Priority assignment node
│   │   │   └── publish.py            # Plane.so task creation node
│   │   ├── prompts/
│   │   │   ├── test_generation.py    # Prompt templates for test creation
│   │   │   ├── priority_assignment.py
│   │   │   └── site_analysis.py      # Prompt for URL-based analysis
│   │   └── llm_provider.py           # Ollama/Gemini abstraction layer
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── engine.py                  # Playwright BFS crawler engine
│   │   ├── element_extractor.py      # DOM element cataloging
│   │   ├── sitemap_builder.py        # Site map construction
│   │   ├── config.py                  # CrawlConfig dataclass
│   │   └── test_generator.py         # LLM-based test generation from crawl
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py                     # FastAPI app factory
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── webhooks.py           # POST /webhooks/plane
│   │   │   ├── crawl.py              # POST /crawl
│   │   │   ├── reports.py            # GET /reports/export-csv
│   │   │   └── health.py             # GET /health
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── webhook.py            # Plane.so webhook payload models
│   │   │   ├── crawl.py              # Crawl request/response models
│   │   │   └── report.py             # Report export models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── test_runner.py        # Async Playwright subprocess launcher
│   │   │   ├── plane_client.py       # Plane.so API client
│   │   │   ├── allure_collector.py   # Allure results mover
│   │   │   └── git_committer.py     # Auto-commit on test success
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── webhook_validator.py  # Signature validation
│   └── common/
│       ├── __init__.py
│       ├── logging.py                 # Structured logging setup
│       └── exceptions.py             # Custom exception classes
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Shared pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_rag_loader.py
│   │   ├── test_rag_retriever.py
│   │   ├── test_agent_state.py
│   │   ├── test_llm_provider.py
│   │   └── test_crawler_engine.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_webhook_endpoint.py
│   │   ├── test_crawl_endpoint.py
│   │   ├── test_agent_flow.py
│   │   └── test_plane_client.py
│   └── e2e/
│       ├── __init__.py
│       ├── conftest.py                # Browser fixtures, base URLs
│       ├── pages/                     # Page Object Model classes
│       │   ├── __init__.py
│       │   ├── base_page.py
│       │   ├── login_page.py
│       │   ├── dashboard_page.py
│       │   └── navigation_page.py
│       ├── test_smoke.py             # Smoke test suite
│       ├── test_regression.py        # Full regression suite
│       └── generated/                # Auto-generated tests from URL crawl
│           ├── __init__.py
│           └── .gitkeep
├── data/
│   ├── stories/                       # User story input documents
│   │   ├── sample_story.md
│   │   └── sample_story.json
│   ├── chroma/                        # ChromaDB persistent storage
│   │   └── .gitkeep
│   └── allure-results/               # Allure test results volume
│       └── .gitkeep
├── scripts/
│   ├── setup_plane.sh                # Plane.so initial setup automation
│   ├── seed_stories.py               # Load sample stories into ChromaDB
│   └── run_tests.sh                  # CLI helper for test execution
├── docker/
│   ├── Dockerfile                     # Main app container
│   ├── Dockerfile.playwright          # Playwright test runner container
│   └── allure/
│       └── Dockerfile                 # Allure server customization
├── docker-compose.yml                 # Full infrastructure definition
├── .env.example                       # Environment variable template
├── .gitignore
├── pyproject.toml                     # Project metadata & dependencies
├── requirements.txt                   # Pinned production dependencies
├── requirements-dev.txt               # Development/test dependencies
├── pytest.ini                         # Pytest configuration
├── README.md
└── LICENSE
```

## Key Directory Purposes

### `src/rag/`
Handles document ingestion, vector embedding, and semantic search. Provides the knowledge base that feeds the LangGraph agent with relevant user story context.

### `src/agent/`
LangGraph state machine orchestrating the flow from story retrieval to test generation to task creation. Contains LLM provider abstraction and prompt templates.

### `src/crawler/`
Playwright-based site discovery engine. Navigates target URLs, extracts interactive elements, builds site maps, and uses LLM to generate test scripts from discovered patterns.

### `src/api/`
FastAPI application handling webhooks from Plane.so, crawl requests, test execution dispatch, and report exports. Acts as the central orchestrator.

### `tests/e2e/pages/`
Page Object Model classes providing reusable abstractions for UI interactions. Both manually authored and auto-generated tests use these.

### `tests/e2e/generated/`
Auto-generated test files produced by the site crawler + LLM analysis pipeline. These are committed to version control once validated.

### `data/`
Persistent data layer including user story inputs, ChromaDB vector storage, and Allure test execution results.

### `docker/`
Container definitions for the application, Playwright test runner (with browsers pre-installed), and Allure server.

## Module Dependencies

```
config/settings.py ──────────────────────────────────────────────────┐
                                                                     │
rag/loader.py ──> rag/splitter.py ──> rag/embeddings.py             │
                                            │                        │
                                            ▼                        │
                                   rag/vectorstore.py                │
                                            │                        │
                                            ▼                        │
                                    rag/retriever.py ───────┐        │
                                                            │        │
agent/llm_provider.py ─────────────────────────────────┐    │        │
                                                       │    │        │
agent/nodes/* ──> agent/prompts/* ──> agent/graph.py <─┤────┘        │
                                            │          │             │
                                            ▼          │             │
crawler/engine.py ──> crawler/element_extractor.py     │             │
         │                       │                     │             │
         ▼                       ▼                     │             │
crawler/sitemap_builder.py ──> crawler/test_generator.py             │
                                            │                        │
                                            ▼                        │
api/routes/* ──> api/services/* ──> api/app.py <─────────────────────┘
```
