# Implementation Tasks: TestOps Pro Frontend Integration

## Phase 1: Foundation & Scaffolding

### Task 1: Frontend Project Setup
- [ ] Create `frontend/` directory and initialize with `package.json` (copy dependencies from TestOps Pro)
- [ ] Create `frontend/tsconfig.json` with TypeScript strict mode
- [ ] Create `frontend/vite.config.ts` with React plugin, Tailwind plugin, and API proxy to `localhost:8000`
- [ ] Create `frontend/index.html` as Vite entry point
- [ ] Create `frontend/src/main.tsx` with React root render
- [ ] Create `frontend/src/index.css` with Tailwind imports and CSS variable definitions (light/dark themes)
- [ ] Create `frontend/src/types.ts` with shared TypeScript type definitions (migrated from TestOps Pro)
- [ ] Install all dependencies: react, react-dom, recharts, lucide-react, motion, tailwindcss, vite, typescript
- [ ] Verify `npm run dev` starts the frontend on port 3000 with HMR working
- [ ] Update root `.gitignore` to include `frontend/node_modules/`, `frontend/dist/`

### Task 2: Backend Database Layer
- [ ] Add `aiosqlite` to `requirements.txt`
- [ ] Create `src/api/db/__init__.py`
- [ ] Create `src/api/db/connection.py` with async SQLite connection pool and initialization
- [ ] Create `src/api/db/migrations/001_initial_schema.sql` with tables: projects, tasks, test_suites, stories, settings, users, system_events
- [ ] Create `src/api/db/migrations/002_seed_default_data.sql` with default admin user and sample project
- [ ] Create `scripts/migrate.py` to apply pending SQL migrations in order
- [ ] Create `src/api/db/repositories/__init__.py` and `src/api/db/repositories/base.py` with base repository pattern
- [ ] Update `src/config/settings.py` to add `DB_PATH`, `JWT_SECRET`, `JWT_EXPIRY_HOURS` settings
- [ ] Update `.env.example` with new environment variables
- [ ] Integrate database initialization into FastAPI lifespan (create tables on startup)

### Task 3: Authentication Backend
- [ ] Add `python-jose[cryptography]` and `passlib[bcrypt]` to `requirements.txt`
- [ ] Create `src/api/schemas/auth.py` with LoginRequest, LoginResponse, UserResponse Pydantic models
- [ ] Create `src/api/db/repositories/user_repo.py` with create_user, get_by_email, verify_password
- [ ] Create `src/api/services/auth_service.py` with JWT token creation, validation, and password hashing
- [ ] Create `src/api/middleware/auth_middleware.py` with cookie-based JWT extraction dependency
- [ ] Create `src/api/routes/auth.py` with `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- [ ] Register auth routes in `src/api/app.py`
- [ ] Add auth dependency to all new `/api/*` routes (except login and health)

## Phase 2: Core Backend API Endpoints

### Task 4: Projects API
- [ ] Create `src/api/schemas/project.py` with ProjectCreate, ProjectUpdate, ProjectResponse models
- [ ] Create `src/api/db/repositories/project_repo.py` with CRUD operations
- [ ] Create `src/api/services/project_service.py` with business logic (health score calculation, event logging)
- [ ] Create `src/api/routes/projects.py` with `GET /api/projects`, `POST /api/projects`, `PATCH /api/projects/{id}`, `DELETE /api/projects/{id}`
- [ ] Register projects routes in `src/api/app.py`
- [ ] Add integration test for projects CRUD endpoint

### Task 5: Tasks (Kanban) API
- [ ] Create `src/api/schemas/task.py` with TaskCreate, TaskUpdate, TaskResponse, TaskMoveRequest models
- [ ] Create `src/api/db/repositories/task_repo.py` with CRUD + filter by column/category/project
- [ ] Create `src/api/services/task_service.py` with business logic (Plane.so sync when configured, event logging)
- [ ] Create `src/api/routes/tasks.py` with `GET /api/tasks`, `POST /api/tasks`, `PATCH /api/tasks/{id}`, `DELETE /api/tasks/{id}`, `PATCH /api/tasks/{id}/move`
- [ ] Register tasks routes in `src/api/app.py`
- [ ] Add integration test for tasks CRUD and move endpoint

### Task 6: Test Suites API
- [ ] Create `src/api/schemas/test_suite.py` with TestSuiteResponse, RunSuiteRequest, SuiteStepResponse models
- [ ] Create `src/api/db/repositories/test_suite_repo.py` with list, get, update_status operations
- [ ] Create `src/api/services/test_suite_service.py` with list suites, trigger run (delegates to existing test_runner), update results
- [ ] Create `src/api/routes/test_suites.py` with `GET /api/test-suites`, `GET /api/test-suites/{id}`, `POST /api/test-suites/{id}/run`
- [ ] Register test suites routes in `src/api/app.py`
- [ ] Wire into existing `test_runner.py` service for actual pytest execution

### Task 7: Stories API
- [ ] Create `src/api/schemas/story.py` with StoryCreate, StoryResponse, SeedRequest models
- [ ] Create `src/api/db/repositories/story_repo.py` with CRUD + mark_indexed operations
- [ ] Create `src/api/services/story_service.py` with create story, trigger RAG indexing (use existing `rag/loader.py` + `rag/vectorstore.py`), list stories
- [ ] Create `src/api/routes/stories.py` with `GET /api/stories`, `POST /api/stories`, `DELETE /api/stories/{id}`, `POST /api/stories/seed`
- [ ] Register stories routes in `src/api/app.py`
- [ ] Add integration test for story creation and RAG indexing trigger

### Task 8: Stats & Reports API
- [ ] Create `src/api/schemas/stats.py` with OverviewStats, VelocityData, FailureBreakdown models
- [ ] Create `src/api/db/repositories/event_repo.py` with recent events, event creation
- [ ] Create `src/api/services/stats_service.py` with aggregate metrics from test_suites, tasks, events tables
- [ ] Create `src/api/routes/stats.py` with `GET /api/stats/overview`, `GET /api/stats/velocity`, `GET /api/stats/failures`
- [ ] Extend existing `src/api/routes/reports.py` with `GET /api/reports/analytics` (combines velocity + failure data for charts)
- [ ] Register stats routes in `src/api/app.py`

### Task 9: Settings API
- [ ] Create `src/api/schemas/settings.py` with SettingsResponse, SettingsUpdate models
- [ ] Create `src/api/db/repositories/settings_repo.py` with get_all, get_by_key, upsert operations
- [ ] Create `src/api/services/settings_service.py` with settings read/write logic
- [ ] Create `src/api/routes/settings.py` with `GET /api/settings`, `PATCH /api/settings`
- [ ] Register settings routes in `src/api/app.py`

## Phase 3: Frontend Core Layout & Navigation

### Task 10: Layout Components & Routing
- [ ] Create `frontend/src/components/layout/AppShell.tsx` with flex layout (sidebar + main content area)
- [ ] Migrate `Header.tsx` from TestOps Pro to `frontend/src/components/layout/Header.tsx` (adapt imports)
- [ ] Migrate `Sidebar.tsx` from TestOps Pro to `frontend/src/components/layout/Sidebar.tsx` (add Stories and Crawl nav items)
- [ ] Create `frontend/src/context/ThemeContext.tsx` (migrate from TestOps Pro)
- [ ] Create `frontend/src/context/AuthContext.tsx` with login/logout state, token management, protected route logic
- [ ] Create `frontend/src/context/AppContext.tsx` for UI-only state (currentView, filters, viewMode)
- [ ] Create `frontend/src/App.tsx` with context providers, auth guard, and view routing
- [ ] Verify layout renders correctly with sidebar navigation switching views

### Task 11: API Client & Shared Utilities
- [ ] Create `frontend/src/services/apiClient.ts` with typed fetch wrapper (GET, POST, PATCH, DELETE), error handling, auth cookie auto-inclusion
- [ ] Create `frontend/src/services/authService.ts` with login(), logout(), getMe() calls
- [ ] Create `frontend/src/hooks/usePolling.ts` generic polling utility (interval, enabled flag, cleanup)
- [ ] Create `frontend/src/utils/formatters.ts` with date, duration, and number formatters
- [ ] Create `frontend/src/utils/constants.ts` with column definitions, categories, priority levels
- [ ] Create `frontend/src/components/shared/LoadingSkeleton.tsx` generic loading placeholder
- [ ] Create `frontend/src/components/shared/Toast.tsx` notification component
- [ ] Create `frontend/src/components/shared/ErrorBoundary.tsx` React error boundary
- [ ] Create `frontend/src/components/shared/EmptyState.tsx` empty list placeholder
- [ ] Create `frontend/src/components/shared/Badge.tsx` status badge component
- [ ] Create `frontend/src/components/shared/Modal.tsx` reusable modal wrapper

### Task 12: Login Screen
- [ ] Create `frontend/src/components/auth/LoginScreen.tsx` (migrate design from TestOps Pro, wire to authService)
- [ ] Implement login form with email + password fields, validation, error display
- [ ] Wire login to `POST /api/auth/login` and store session in AuthContext
- [ ] Implement logout button in Header that calls `POST /api/auth/logout`
- [ ] Add redirect to login when AuthContext detects no valid session

## Phase 4: Frontend Views — Data Connected

### Task 13: Overview Dashboard (Connected)
- [ ] Create `frontend/src/services/reportsService.ts` with getOverviewStats(), getVelocity(), getFailures()
- [ ] Create `frontend/src/hooks/useStats.ts` with polling to `GET /api/stats/overview`
- [ ] Migrate `OverviewDashboard.tsx` from TestOps Pro, refactor into sub-components:
  - [ ] `frontend/src/components/dashboard/StatCard.tsx` — reusable metric card
  - [ ] `frontend/src/components/dashboard/ProjectCard.tsx` — project summary card
  - [ ] `frontend/src/components/dashboard/SystemEventsFeed.tsx` — events list
  - [ ] `frontend/src/components/dashboard/TestStreamTable.tsx` — live suites table
- [ ] Replace hardcoded mock data with `useStats()` hook data
- [ ] Add loading skeletons and error states

### Task 14: Kanban Board (Connected)
- [ ] Create `frontend/src/services/tasksService.ts` with getTasks(), createTask(), updateTask(), deleteTask(), moveTask()
- [ ] Create `frontend/src/hooks/useTasks.ts` with CRUD operations and optimistic updates
- [ ] Migrate KanbanBoard from TestOps Pro, refactor into sub-components:
  - [ ] `frontend/src/components/kanban/KanbanBoard.tsx` — main container
  - [ ] `frontend/src/components/kanban/KanbanColumn.tsx` — single column
  - [ ] `frontend/src/components/kanban/TaskCard.tsx` — task card
  - [ ] `frontend/src/components/kanban/TaskModal.tsx` — create/edit modal
  - [ ] `frontend/src/components/kanban/KanbanFilters.tsx` — filters + view switcher
- [ ] Replace context-based task state with `useTasks()` hook
- [ ] Wire create/edit/delete/move operations to backend API
- [ ] Verify task persistence across page reloads

### Task 15: Test Suites View (Connected)
- [ ] Create `frontend/src/services/testSuitesService.ts` with getTestSuites(), getTestSuite(), runSuite()
- [ ] Create `frontend/src/hooks/useTestSuites.ts` with list + run + polling for status updates
- [ ] Migrate TestSuites from TestOps Pro, refactor into sub-components:
  - [ ] `frontend/src/components/tests/TestSuites.tsx` — main layout
  - [ ] `frontend/src/components/tests/SuiteListItem.tsx` — suite card
  - [ ] `frontend/src/components/tests/SuiteConsole.tsx` — step inspector + terminal
  - [ ] `frontend/src/components/tests/StepRow.tsx` — individual step display
- [ ] Replace mock `runTestSuite` with real API call to `POST /api/test-suites/{id}/run`
- [ ] Implement polling for suite status while RUNNING
- [ ] Display real step results from backend

### Task 16: Execution Reports (Connected)
- [ ] Create `frontend/src/hooks/useReports.ts` with velocity, failures, pass rate data fetching
- [ ] Migrate ExecutionReports from TestOps Pro, refactor into sub-components:
  - [ ] `frontend/src/components/reports/ExecutionReports.tsx` — main layout
  - [ ] `frontend/src/components/reports/VelocityChart.tsx` — area chart
  - [ ] `frontend/src/components/reports/FailurePieChart.tsx` — pie chart
  - [ ] `frontend/src/components/reports/PassRateChart.tsx` — bar chart
- [ ] Replace hardcoded chart data with `useReports()` hook data
- [ ] Wire CSV export button to `GET /reports/export-csv` (existing endpoint)
- [ ] Add date range filter controls

### Task 17: Projects View (Connected)
- [ ] Create `frontend/src/services/projectsService.ts` with getProjects(), createProject(), updateProject()
- [ ] Create `frontend/src/hooks/useProjects.ts` with CRUD operations
- [ ] Migrate AllProjects and CreateProject from TestOps Pro:
  - [ ] `frontend/src/components/projects/AllProjects.tsx` — projects grid
  - [ ] `frontend/src/components/projects/CreateProject.tsx` — creation wizard
  - [ ] `frontend/src/components/projects/ProjectDetailCard.tsx` — project card
- [ ] Replace mock project data with `useProjects()` hook
- [ ] Wire CreateProject form to `POST /api/projects`
- [ ] Verify project creation persists and appears in list

## Phase 5: New Frontend Views

### Task 18: User Stories Management View
- [ ] Create `frontend/src/services/storiesService.ts` with getStories(), createStory(), deleteStory(), seedStories()
- [ ] Create `frontend/src/hooks/useStories.ts` with CRUD + seeding operations
- [ ] Create `frontend/src/components/stories/StoriesPage.tsx` — main layout with list + upload panel
- [ ] Create `frontend/src/components/stories/StoryCard.tsx` — story display with metadata badges (epic, feature, indexed status)
- [ ] Create `frontend/src/components/stories/StoryUploadForm.tsx` — form with title, content (textarea), format toggle (MD/JSON), metadata fields
- [ ] Create `frontend/src/components/stories/StoryDetailModal.tsx` — full content view + generated scenarios count
- [ ] Add "Seed All" button that calls `POST /api/stories/seed` to trigger RAG indexing
- [ ] Add indicator showing which stories have been indexed in ChromaDB
- [ ] Add sidebar navigation item for "Stories" view

### Task 19: Site Crawl UI View
- [ ] Create `frontend/src/services/crawlService.ts` with triggerCrawl(), getCrawlStatus()
- [ ] Create `frontend/src/components/crawl/CrawlPage.tsx` — main layout with form + results
- [ ] Create `frontend/src/components/crawl/CrawlForm.tsx` — URL input, max_depth slider, max_pages input, generate_tests checkbox
- [ ] Create `frontend/src/components/crawl/CrawlProgress.tsx` — progress indicator during crawl (pages discovered count, elapsed time)
- [ ] Create `frontend/src/components/crawl/CrawlResults.tsx` — listing of generated files (POM classes, test scripts) with code preview
- [ ] Wire form submission to `POST /crawl` (existing endpoint)
- [ ] Display crawl results including site map and element counts
- [ ] Add sidebar navigation item for "Crawl" view

### Task 20: Settings View (Connected)
- [ ] Create `frontend/src/services/settingsService.ts` with getSettings(), updateSettings()
- [ ] Create `frontend/src/hooks/useSettings.ts` with read/write operations
- [ ] Migrate SettingsPage from TestOps Pro, refactor into sub-components:
  - [ ] `frontend/src/components/settings/SettingsPage.tsx` — main layout
  - [ ] `frontend/src/components/settings/ThemeSettings.tsx` — light/dark toggle + color palette
  - [ ] `frontend/src/components/settings/WebhookSettings.tsx` — Slack URL, email alerts
  - [ ] `frontend/src/components/settings/ApiKeySettings.tsx` — API key display + copy
- [ ] Wire theme changes to ThemeContext (already client-side)
- [ ] Wire webhook/notification settings to `PATCH /api/settings`
- [ ] Add save confirmation toast on successful update

## Phase 6: Integration & Polish

### Task 21: Docker & Deployment Configuration
- [ ] Update `docker/Dockerfile` to multi-stage build: Node build stage + Python production stage
- [ ] Create `docker/Dockerfile.frontend` for standalone frontend dev container (optional)
- [ ] Update `docker-compose.yml` to add `frontend` service (dev mode with volume mount + HMR)
- [ ] Update `docker-compose.yml` to configure `app` service to serve built frontend in production mode
- [ ] Update `src/api/app.py` to mount `frontend/dist/` as static files when `ENVIRONMENT=production`
- [ ] Add SPA fallback (serve `index.html` for non-API routes) in production mode
- [ ] Verify `docker compose up` starts both frontend and backend correctly
- [ ] Update `.env.example` with all new variables (JWT_SECRET, DB_PATH, FRONTEND_URL)

### Task 22: End-to-End Verification
- [ ] Run database migrations and verify all tables created
- [ ] Create a user via migration seed and verify login works
- [ ] Create a project via UI and verify persistence
- [ ] Create tasks in Kanban and verify CRUD operations
- [ ] Upload a user story and verify RAG indexing triggers
- [ ] Trigger a crawl from UI and verify results display
- [ ] Run a test suite from UI and verify status updates
- [ ] Verify dashboard stats reflect real data
- [ ] Verify settings changes persist across page reloads
- [ ] Verify dark/light theme switching works
- [ ] Test logout and re-login flow

### Task 23: Frontend Build & Production Optimization
- [ ] Verify `npm run build` produces optimized bundle in `frontend/dist/`
- [ ] Verify production bundle size < 500KB gzipped
- [ ] Add `npm run lint` (TypeScript type checking) to CI/build step
- [ ] Remove all references to `mockData.ts` (or keep as development fallback)
- [ ] Verify all views work with production build served from FastAPI
- [ ] Update `README.md` with frontend setup instructions, dev workflow, and production deployment

### Task 24: Documentation & Cleanup
- [ ] Update root `README.md` with frontend section: setup, dev server, build, environment variables
- [ ] Add API endpoint documentation for all new routes (curl examples)
- [ ] Create `frontend/README.md` with component architecture overview
- [ ] Create `.kiro/steering/frontend-standards.md` with React/TypeScript conventions
- [ ] Remove any unused TestOps Pro code that wasn't migrated (if applicable)
- [ ] Verify all success metrics from product.md are achievable with current implementation
