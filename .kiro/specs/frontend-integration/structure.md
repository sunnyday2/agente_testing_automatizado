# Project Structure: TestOps Pro Frontend Integration

## Updated Root Directory Layout

```
agente_testing_automatizado/
├── .kiro/
│   ├── specs/
│   │   ├── qa-automation-agent/         # Original backend spec
│   │   │   ├── product.md
│   │   │   ├── tech.md
│   │   │   ├── structure.md
│   │   │   └── tasks.md
│   │   └── frontend-integration/        # THIS spec
│   │       ├── product.md
│   │       ├── tech.md
│   │       ├── structure.md
│   │       └── tasks.md
│   └── steering/
│       ├── coding-standards.md
│       ├── testing-standards.md
│       ├── agent-architecture.md
│       ├── infrastructure.md
│       └── frontend-standards.md        # NEW: Frontend coding conventions
├── frontend/                            # NEW: React frontend application
│   ├── index.html                       # Vite entry HTML
│   ├── package.json                     # Frontend dependencies
│   ├── tsconfig.json                    # TypeScript configuration
│   ├── vite.config.ts                   # Vite config with API proxy
│   ├── tailwind.config.ts              # Tailwind CSS configuration (if needed beyond v4)
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.tsx                     # React entry point
│   │   ├── App.tsx                      # Root component with routing
│   │   ├── index.css                    # Global styles + Tailwind imports + CSS variables
│   │   ├── types.ts                     # Shared TypeScript type definitions
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx           # Top navigation bar with user info
│   │   │   │   ├── Sidebar.tsx          # Left navigation menu
│   │   │   │   └── AppShell.tsx         # Layout wrapper (header + sidebar + main)
│   │   │   ├── dashboard/
│   │   │   │   ├── OverviewDashboard.tsx    # Main dashboard view
│   │   │   │   ├── StatCard.tsx             # Reusable metric card
│   │   │   │   ├── ProjectCard.tsx          # Project summary card
│   │   │   │   ├── SystemEventsFeed.tsx     # Event log list
│   │   │   │   └── TestStreamTable.tsx      # Live test status table
│   │   │   ├── kanban/
│   │   │   │   ├── KanbanBoard.tsx          # Main Kanban view
│   │   │   │   ├── KanbanColumn.tsx         # Single column container
│   │   │   │   ├── TaskCard.tsx             # Individual task card
│   │   │   │   ├── TaskModal.tsx            # Create/edit task modal
│   │   │   │   └── KanbanFilters.tsx        # Filter chips + view switcher
│   │   │   ├── tests/
│   │   │   │   ├── TestSuites.tsx           # Test suite management view
│   │   │   │   ├── SuiteListItem.tsx        # Suite card in left panel
│   │   │   │   ├── SuiteConsole.tsx         # Step inspector + terminal output
│   │   │   │   └── StepRow.tsx              # Individual assertion step row
│   │   │   ├── reports/
│   │   │   │   ├── ExecutionReports.tsx     # Analytics & charts view
│   │   │   │   ├── VelocityChart.tsx        # Daily volume area chart
│   │   │   │   ├── FailurePieChart.tsx      # Root cause breakdown
│   │   │   │   └── PassRateChart.tsx        # Environment pass rate bars
│   │   │   ├── projects/
│   │   │   │   ├── AllProjects.tsx          # Projects list view
│   │   │   │   ├── CreateProject.tsx        # New project wizard
│   │   │   │   └── ProjectDetailCard.tsx    # Project info card
│   │   │   ├── stories/                     # NEW: User story management
│   │   │   │   ├── StoriesPage.tsx          # Stories list + upload view
│   │   │   │   ├── StoryCard.tsx            # Individual story display
│   │   │   │   ├── StoryUploadForm.tsx      # Upload/create story form
│   │   │   │   └── StoryDetailModal.tsx     # View story content + metadata
│   │   │   ├── crawl/                       # NEW: Site crawl UI
│   │   │   │   ├── CrawlPage.tsx            # Crawl trigger + results view
│   │   │   │   ├── CrawlForm.tsx            # URL input + options form
│   │   │   │   ├── CrawlProgress.tsx        # Real-time crawl status
│   │   │   │   └── CrawlResults.tsx         # Generated files listing
│   │   │   ├── settings/
│   │   │   │   ├── SettingsPage.tsx         # Settings layout
│   │   │   │   ├── ThemeSettings.tsx        # Light/dark mode toggle
│   │   │   │   ├── WebhookSettings.tsx      # Notification configuration
│   │   │   │   └── ApiKeySettings.tsx       # Credential management
│   │   │   ├── auth/
│   │   │   │   └── LoginScreen.tsx          # Authentication form
│   │   │   └── shared/
│   │   │       ├── LoadingSkeleton.tsx       # Generic loading placeholder
│   │   │       ├── ErrorBoundary.tsx        # React error boundary
│   │   │       ├── Toast.tsx                # Notification toast component
│   │   │       ├── Modal.tsx                # Reusable modal wrapper
│   │   │       ├── Badge.tsx                # Status badge component
│   │   │       └── EmptyState.tsx           # Empty list placeholder
│   │   ├── context/
│   │   │   ├── ThemeContext.tsx             # Dark/light mode state
│   │   │   ├── AuthContext.tsx              # NEW: Auth state + login/logout
│   │   │   └── AppContext.tsx              # UI state (view, filters, local state)
│   │   ├── hooks/                           # NEW: Data-fetching hooks
│   │   │   ├── useProjects.ts              # Projects CRUD + polling
│   │   │   ├── useTasks.ts                 # Tasks CRUD + Kanban state
│   │   │   ├── useTestSuites.ts            # Test suites + execution
│   │   │   ├── useStories.ts              # Stories CRUD + indexing
│   │   │   ├── useReports.ts              # Analytics data fetching
│   │   │   ├── useStats.ts                # Dashboard overview stats
│   │   │   ├── useSettings.ts             # Settings read/write
│   │   │   └── usePolling.ts              # Generic polling utility hook
│   │   ├── services/                        # NEW: API communication layer
│   │   │   ├── apiClient.ts               # Base fetch wrapper with auth
│   │   │   ├── authService.ts             # Login, logout, refresh token
│   │   │   ├── projectsService.ts         # Projects API calls
│   │   │   ├── tasksService.ts            # Tasks API calls
│   │   │   ├── testSuitesService.ts       # Test suites API calls
│   │   │   ├── storiesService.ts          # Stories API calls
│   │   │   ├── reportsService.ts          # Reports/analytics API calls
│   │   │   ├── crawlService.ts            # Crawl trigger API calls
│   │   │   └── settingsService.ts         # Settings API calls
│   │   └── utils/
│   │       ├── formatters.ts              # Date, number, duration formatters
│   │       └── constants.ts               # App-wide constants (columns, categories)
│   └── dist/                               # Built output (gitignored)
├── src/                                     # EXISTING: Python backend
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                     # Extended with frontend/auth settings
│   │   └── database.py                     # NEW: SQLite connection + init
│   ├── rag/                                 # EXISTING: unchanged
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── splitter.py
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   └── retriever.py
│   ├── agent/                               # EXISTING: unchanged
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── graph.py
│   │   ├── nodes/
│   │   ├── prompts/
│   │   └── llm_provider.py
│   ├── crawler/                             # EXISTING: unchanged
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── element_extractor.py
│   │   ├── sitemap_builder.py
│   │   ├── config.py
│   │   └── test_generator.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py                          # Extended: static file serving + new routes
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── webhooks.py                # EXISTING
│   │   │   ├── crawl.py                   # EXISTING
│   │   │   ├── reports.py                 # EXISTING: extended with analytics
│   │   │   ├── health.py                  # EXISTING
│   │   │   ├── auth.py                    # NEW: login, me, refresh
│   │   │   ├── tasks.py                   # NEW: CRUD for Kanban tasks
│   │   │   ├── projects.py               # NEW: CRUD for projects
│   │   │   ├── stories.py                # NEW: CRUD + seed for stories
│   │   │   ├── test_suites.py            # NEW: list + run suites
│   │   │   ├── stats.py                  # NEW: aggregated dashboard stats
│   │   │   └── settings.py               # NEW: settings CRUD
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── webhook.py                 # EXISTING
│   │   │   ├── crawl.py                   # EXISTING
│   │   │   ├── common.py                  # EXISTING
│   │   │   ├── auth.py                    # NEW: login request/response
│   │   │   ├── task.py                    # NEW: task CRUD models
│   │   │   ├── project.py                # NEW: project models
│   │   │   ├── story.py                  # NEW: story models
│   │   │   ├── test_suite.py             # NEW: test suite models
│   │   │   ├── stats.py                  # NEW: dashboard stats model
│   │   │   └── settings.py               # NEW: settings model
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── test_runner.py            # EXISTING
│   │   │   ├── plane_client.py           # EXISTING
│   │   │   ├── allure_collector.py       # EXISTING
│   │   │   ├── git_committer.py          # EXISTING
│   │   │   ├── auth_service.py           # NEW: JWT creation/validation
│   │   │   ├── task_service.py           # NEW: task CRUD logic
│   │   │   ├── project_service.py        # NEW: project CRUD logic
│   │   │   ├── story_service.py          # NEW: story management + RAG trigger
│   │   │   ├── test_suite_service.py     # NEW: suite management + execution
│   │   │   ├── stats_service.py          # NEW: metrics aggregation
│   │   │   └── settings_service.py       # NEW: settings persistence
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── webhook_validator.py      # EXISTING
│   │   │   └── auth_middleware.py        # NEW: JWT cookie extraction
│   │   └── db/                            # NEW: Database layer
│   │       ├── __init__.py
│   │       ├── connection.py              # SQLite async connection pool
│   │       ├── migrations/
│   │       │   ├── 001_initial_schema.sql
│   │       │   ├── 002_seed_default_data.sql
│   │       │   └── ...
│   │       └── repositories/
│   │           ├── __init__.py
│   │           ├── base.py                # Base repository pattern
│   │           ├── task_repo.py           # Task queries
│   │           ├── project_repo.py        # Project queries
│   │           ├── story_repo.py          # Story queries
│   │           ├── test_suite_repo.py     # Test suite queries
│   │           ├── user_repo.py           # User queries
│   │           ├── settings_repo.py       # Settings queries
│   │           └── event_repo.py          # System events queries
│   └── common/                             # EXISTING: unchanged
│       ├── __init__.py
│       ├── logging.py
│       └── exceptions.py
├── data/
│   ├── stories/                            # EXISTING
│   ├── chroma/                             # EXISTING
│   ├── allure-results/                     # EXISTING
│   └── qa_agent.db                         # NEW: SQLite database file
├── scripts/
│   ├── setup_plane.sh                      # EXISTING
│   ├── seed_stories.py                     # EXISTING
│   ├── run_tests.sh                        # EXISTING
│   └── migrate.py                          # NEW: Database migration runner
├── docker/
│   ├── Dockerfile                          # UPDATED: multi-stage with frontend build
│   ├── Dockerfile.playwright               # EXISTING
│   ├── Dockerfile.frontend                 # NEW: standalone frontend dev container
│   └── allure/
│       └── Dockerfile                      # EXISTING
├── tests/                                   # EXISTING: extended
│   ├── unit/
│   │   ├── ... (existing)
│   │   ├── test_auth_service.py           # NEW
│   │   ├── test_task_service.py           # NEW
│   │   └── test_project_service.py        # NEW
│   ├── integration/
│   │   ├── ... (existing)
│   │   ├── test_tasks_endpoint.py         # NEW
│   │   ├── test_stories_endpoint.py       # NEW
│   │   └── test_auth_endpoint.py          # NEW
│   └── e2e/                                # EXISTING
├── docker-compose.yml                      # UPDATED: add frontend service
├── .env.example                            # UPDATED: add JWT_SECRET, DB_PATH
├── .gitignore                              # UPDATED: add frontend/dist, node_modules
├── pyproject.toml                          # EXISTING
├── requirements.txt                        # UPDATED: add aiosqlite, python-jose, passlib
├── requirements-dev.txt                    # EXISTING
├── pytest.ini                              # EXISTING
├── README.md                               # UPDATED: frontend instructions
└── LICENSE                                 # EXISTING
```

## Key Directory Purposes

### `frontend/`
Self-contained React application. Built with Vite, served as static files in production. Contains all UI components, state management, API client layer, and styling.

### `frontend/src/components/`
Organized by feature/view rather than by type. Each subdirectory maps to a top-level view in the application (dashboard, kanban, tests, reports, etc.). Shared components live in `shared/`.

### `frontend/src/hooks/`
Custom React hooks that encapsulate data fetching, polling, and server state management. Each hook corresponds to a backend resource (projects, tasks, test suites, etc.) and provides loading/error states.

### `frontend/src/services/`
API communication layer. Each service file wraps fetch calls to a specific backend resource. The `apiClient.ts` base handles auth headers, error parsing, and response typing.

### `frontend/src/context/`
React Context providers for cross-cutting concerns: theme (light/dark), auth (user session), and app-level UI state (current view, filters). Does NOT store server data — that lives in hooks.

### `src/api/routes/` (New Routes)
New FastAPI route modules for CRUD operations needed by the frontend. Each follows the same pattern: router with typed schemas, dependency injection, and service delegation.

### `src/api/db/`
Database layer with SQLite connection management, versioned SQL migrations, and repository classes that encapsulate query logic. Repositories are injected into services via FastAPI's dependency system.

### `src/api/services/` (New Services)
Business logic layer between routes and repositories. Handles validation, cross-service coordination (e.g., story service triggers RAG indexing), and event logging.

## Module Dependencies

### Frontend Dependency Graph

```
main.tsx
  └── App.tsx
        ├── context/ThemeContext.tsx
        ├── context/AuthContext.tsx ──────────────────────────┐
        ├── context/AppContext.tsx                            │
        │                                                     │
        ├── components/layout/AppShell.tsx                    │
        │     ├── components/layout/Header.tsx                │
        │     └── components/layout/Sidebar.tsx               │
        │                                                     │
        ├── components/dashboard/OverviewDashboard.tsx        │
        │     └── hooks/useStats.ts                          │
        │           └── services/apiClient.ts ◄──────────────┘
        │                                                     
        ├── components/kanban/KanbanBoard.tsx                 
        │     └── hooks/useTasks.ts                          
        │           └── services/tasksService.ts             
        │                 └── services/apiClient.ts          
        │                                                     
        ├── components/tests/TestSuites.tsx                   
        │     └── hooks/useTestSuites.ts                     
        │           └── services/testSuitesService.ts        
        │                                                     
        ├── components/reports/ExecutionReports.tsx           
        │     └── hooks/useReports.ts                        
        │           └── services/reportsService.ts           
        │                                                     
        ├── components/stories/StoriesPage.tsx                
        │     └── hooks/useStories.ts                        
        │           └── services/storiesService.ts           
        │                                                     
        ├── components/crawl/CrawlPage.tsx                   
        │     └── services/crawlService.ts                   
        │                                                     
        ├── components/projects/AllProjects.tsx               
        │     └── hooks/useProjects.ts                       
        │           └── services/projectsService.ts          
        │                                                     
        └── components/settings/SettingsPage.tsx              
              └── hooks/useSettings.ts                       
                    └── services/settingsService.ts          
```

### Backend Dependency Graph (New Modules)

```
src/api/app.py
  │
  ├── routes/auth.py ──────────> services/auth_service.py ──> db/repositories/user_repo.py
  │                                       │
  │                                       └──> middleware/auth_middleware.py
  │
  ├── routes/tasks.py ─────────> services/task_service.py ──> db/repositories/task_repo.py
  │                                       │
  │                                       └──> services/plane_client.py (optional sync)
  │
  ├── routes/projects.py ──────> services/project_service.py ──> db/repositories/project_repo.py
  │
  ├── routes/stories.py ───────> services/story_service.py ──> db/repositories/story_repo.py
  │                                       │
  │                                       └──> rag/loader.py ──> rag/vectorstore.py
  │
  ├── routes/test_suites.py ───> services/test_suite_service.py ──> db/repositories/test_suite_repo.py
  │                                       │
  │                                       └──> services/test_runner.py (existing)
  │
  ├── routes/stats.py ─────────> services/stats_service.py
  │                                       │
  │                                       ├──> db/repositories/task_repo.py
  │                                       ├──> db/repositories/test_suite_repo.py
  │                                       └──> db/repositories/event_repo.py
  │
  ├── routes/settings.py ──────> services/settings_service.py ──> db/repositories/settings_repo.py
  │
  └── db/connection.py ─────────> data/qa_agent.db (SQLite file)
        │
        └── db/migrations/*.sql (applied at startup)
```

### Cross-Boundary Communication

```
┌──────────────────┐         HTTP/JSON          ┌──────────────────┐
│                  │  ──────────────────────────>│                  │
│   Frontend       │  GET/POST/PATCH/DELETE      │   Backend        │
│   (port 3000)    │  /api/*                    │   (port 8000)    │
│                  │  <──────────────────────────│                  │
└──────────────────┘     JSON responses          └──────────────────┘
                              │
                    Vite proxy (dev)
                    or nginx (prod)
                    or FastAPI static (simple prod)
```

## File Naming Conventions

### Frontend
- Components: `PascalCase.tsx` (e.g., `KanbanBoard.tsx`)
- Hooks: `camelCase.ts` with `use` prefix (e.g., `useTasks.ts`)
- Services: `camelCase.ts` with `Service` suffix (e.g., `tasksService.ts`)
- Types: `camelCase.ts` (e.g., `types.ts`)
- Utilities: `camelCase.ts` (e.g., `formatters.ts`)

### Backend (New Files)
- Routes: `snake_case.py` (e.g., `test_suites.py`)
- Services: `snake_case.py` with `_service` suffix (e.g., `task_service.py`)
- Repositories: `snake_case.py` with `_repo` suffix (e.g., `task_repo.py`)
- Schemas: `snake_case.py` (e.g., `task.py`)
- Migrations: `NNN_description.sql` (e.g., `001_initial_schema.sql`)
