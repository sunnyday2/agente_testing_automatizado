# Product Requirements: TestOps Pro Frontend Integration

## Problem Statement
The QA Automation Agent currently operates as a headless backend system with no dedicated user interface. Users must interact through CLI commands (`python scripts/seed_stories.py`), raw `curl` calls to the API, or third-party dashboards (Allure, Plane.so) that don't provide a unified experience. This creates friction for non-technical team members (PMs, QA leads) who need visibility into test generation, execution status, and project management without terminal access.

## Proposed Solution
Integrate the "TestOps Pro" React frontend as the unified web interface for the QA Automation Agent. This frontend will connect directly to the existing FastAPI backend, replacing mock data with real API calls, and extending both frontend and backend where needed to provide:
- A visual dashboard for test execution metrics and system health
- A Kanban board for managing test tasks (mirroring/replacing Plane.so dependency)
- A test suite management panel with one-click execution
- Execution reports with charts and analytics
- Project creation and configuration
- User story management (upload, view, seed to RAG)
- Site crawl triggering from a form UI
- Settings management (API keys, webhook config, theme)

## User Personas

### QA Lead / Manager
- Needs a single dashboard to monitor all testing activity
- Wants to trigger test suites and crawls without CLI access
- Requires visual reports (charts, pass rates, failure breakdowns)
- Needs to manage projects and configure integrations via UI

### Product Manager
- Wants to upload user stories directly from the browser
- Needs visibility into which stories have generated tests
- Requires accessible dashboards without technical setup
- Wants to track task progression through Kanban view

### Developer
- Needs quick access to test execution status and logs
- Wants to trigger crawls on staging URLs from the UI
- Requires export capabilities (CSV, JSON) for sprint metrics
- Needs to see test step details and failure logs inline

### QA Engineer
- Needs to view and manage auto-generated test suites
- Wants to re-run specific suites or individual tests from UI
- Requires real-time execution feedback (running/pass/fail states)
- Needs to inspect step-by-step assertion results

## Functional Requirements

### FR-1: Overview Dashboard
- The frontend SHALL display aggregate test metrics (total tests, passed, failed, in-progress)
- The frontend SHALL show recent project cards with health scores and status indicators
- The frontend SHALL display a system events feed with real-time status updates
- The frontend SHALL show weekly velocity metrics (tests/day, trend)
- The frontend SHALL provide a Global Test Stream table with live suite statuses
- The backend SHALL expose a `GET /api/stats/overview` endpoint aggregating metrics

### FR-2: Kanban Task Board
- The frontend SHALL display tasks in columns: IDEAS/PLANNING, BACKLOG, TO DO, IN PROGRESS, REVIEW/TESTING, DONE
- The frontend SHALL support creating, editing, moving, and deleting tasks
- The frontend SHALL support filtering tasks by category and business group
- The frontend SHALL support multiple view modes (Board, List, Compact, Swim Lanes)
- The backend SHALL expose CRUD endpoints for tasks: `GET/POST/PATCH/DELETE /api/tasks`
- The backend SHALL sync task state with Plane.so when configured (bidirectional)

### FR-3: Test Suite Management
- The frontend SHALL list all registered test suites with status, duration, and executor info
- The frontend SHALL allow running individual suites or all suites via button click
- The frontend SHALL display step-by-step execution results with logs per suite
- The frontend SHALL show a simulated terminal console for execution output
- The backend SHALL expose `GET /api/test-suites` and `POST /api/test-suites/{id}/run`

### FR-4: Execution Reports & Analytics
- The frontend SHALL display daily test execution volume charts (area chart)
- The frontend SHALL display failure root cause breakdown (pie chart)
- The frontend SHALL display pass rate stability by environment (bar chart)
- The frontend SHALL show top-level metrics (overall pass rate, MTTD, active regressions)
- The frontend SHALL support CSV/JSON export of analytics data
- The backend SHALL expose `GET /api/reports/analytics` with aggregated chart data

### FR-5: Project Management
- The frontend SHALL allow creating new projects with name, description, environment, visibility
- The frontend SHALL support configuring integrations per project (Jenkins, Slack, Jira, S3)
- The frontend SHALL display all projects with health scores, status, and member info
- The backend SHALL expose `GET/POST /api/projects` and `PATCH /api/projects/{id}`

### FR-6: User Story Management (NEW)
- The frontend SHALL provide a form to upload user stories (Markdown text or JSON)
- The frontend SHALL list all ingested stories with metadata (epic, feature, role)
- The frontend SHALL show which stories have generated test scenarios
- The frontend SHALL allow triggering RAG re-indexing from the UI
- The backend SHALL expose `GET/POST /api/stories` and `POST /api/stories/seed`

### FR-7: Site Crawl UI (NEW)
- The frontend SHALL provide a form to submit a URL for crawling with configuration options (max_depth, max_pages, generate_tests flag)
- The frontend SHALL display crawl progress and results (pages discovered, elements found)
- The frontend SHALL show generated POM classes and test scripts after crawl completes
- The existing `POST /crawl` endpoint SHALL be consumed by the frontend

### FR-8: Settings & Configuration
- The frontend SHALL provide theme switching (light/dark mode)
- The frontend SHALL allow configuring webhook URLs (Slack, etc.)
- The frontend SHALL display and manage API access credentials
- The frontend SHALL allow configuring notification preferences
- The backend SHALL expose `GET/PATCH /api/settings` for persisted configuration

### FR-9: Authentication & Session
- The frontend SHALL provide a login screen with email-based authentication
- The frontend SHALL maintain user session state across page reloads
- The frontend SHALL display user profile info in the header
- The backend SHALL expose `POST /api/auth/login` and `GET /api/auth/me`

## Non-Functional Requirements

### NFR-1: Performance
- Frontend initial load (LCP) SHALL be < 2 seconds on broadband
- API responses for dashboard data SHALL return within 500ms
- Real-time status updates SHALL reflect within 3 seconds of backend state change
- Frontend bundle size SHALL be < 500KB gzipped

### NFR-2: Responsiveness
- The frontend SHALL be fully usable on screens >= 768px (tablet and desktop)
- The sidebar SHALL collapse on smaller viewports
- Charts and tables SHALL be horizontally scrollable on constrained widths

### NFR-3: Accessibility
- All interactive elements SHALL be keyboard-navigable
- Color contrast SHALL meet WCAG 2.1 AA minimum ratios
- Status indicators SHALL not rely solely on color (use icons + text)
- Form inputs SHALL have associated labels

### NFR-4: Browser Compatibility
- The frontend SHALL support latest 2 versions of Chrome, Firefox, Safari, Edge
- The frontend SHALL work without JavaScript service workers (progressive enhancement)

### NFR-5: Developer Experience
- Frontend dev server SHALL support hot module replacement (HMR)
- Frontend SHALL use TypeScript strict mode for type safety
- API integration SHALL use typed fetch wrappers with error handling

### NFR-6: Security
- API calls SHALL include authentication tokens in headers
- Sensitive settings (API keys) SHALL be masked in the UI by default
- CORS SHALL be configured to allow only the frontend origin in production
- No secrets SHALL be stored in frontend code or localStorage (use httpOnly cookies or short-lived tokens)

## Success Metrics
- 100% of existing mock views render correctly with real backend data
- All CRUD operations (tasks, projects, stories) persist across page reloads
- Test suite execution triggered from UI completes and updates status in < 30 seconds
- Dashboard loads within 2 seconds with up to 50 projects and 200 test suites
- Zero console errors in production build
- All forms validate input and display meaningful error messages
