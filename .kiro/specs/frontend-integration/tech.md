# Technical Design: TestOps Pro Frontend Integration

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     QA Automation Agent — Full Stack Architecture                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    TestOps Pro Frontend (React + Vite)                     │  │
│  │                                                                           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │ Overview │ │  Kanban  │ │  Tests   │ │ Reports  │ │  Settings    │   │  │
│  │  │Dashboard │ │  Board   │ │  Suites  │ │ Analytics│ │  & Config    │   │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │  │
│  │       │             │            │            │               │           │  │
│  │  ┌────┴─────────────┴────────────┴────────────┴───────────────┴────────┐  │  │
│  │  │              API Client Layer (typed fetch + error handling)         │  │  │
│  │  │         src/frontend/services/apiClient.ts                          │  │  │
│  │  └────────────────────────────┬────────────────────────────────────────┘  │  │
│  └───────────────────────────────┼───────────────────────────────────────────┘  │
│                                  │ HTTP (JSON)                                   │
│                                  │ Port 3000 → Proxy → Port 8000                 │
│                                  ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Backend (Existing + New Endpoints)              │  │
│  │                                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  NEW API Routes (src/api/routes/)                                   │  │  │
│  │  │  /api/auth/*  │  /api/stats/*  │  /api/tasks/*  │  /api/stories/*   │  │  │
│  │  │  /api/projects/*  │  /api/test-suites/*  │  /api/reports/analytics  │  │  │
│  │  │  /api/settings/*                                                    │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │  EXISTING Routes                                                    │  │  │
│  │  │  /health  │  /crawl  │  /webhooks/plane  │  /reports/export-csv     │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │  │
│  │  │  LangGraph │  │    RAG     │  │  Crawler   │  │  Test Runner       │  │  │
│  │  │   Agent    │  │  ChromaDB  │  │  Playwright│  │  (pytest subprocess)│  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         Data & Infrastructure Layer                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │  │
│  │  │  SQLite    │  │  ChromaDB  │  │   Allure   │  │  Plane.so          │  │  │
│  │  │ (app state)│  │ (vectors)  │  │  (reports) │  │  (optional sync)   │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Technology Decisions

### TD-1: React 19 + TypeScript + Vite as Frontend Stack
**Decision:** Adopt the existing TestOps Pro stack: React 19, TypeScript 5.8, Vite 6, Tailwind CSS 4.
**Rationale:**
- Already built and proven in the TestOps Pro prototype — no need to rewrite
- Vite provides fast HMR and optimized production builds
- TypeScript strict mode catches integration bugs at compile time
- Tailwind CSS 4 offers utility-first styling with CSS variables for theming
- React 19 supports concurrent features and improved Suspense

**Key dependencies from TestOps Pro:**
- `react` / `react-dom` ^19.0.1
- `recharts` ^3.10.0 (charting)
- `lucide-react` ^0.546.0 (icons)
- `motion` ^12.23.24 (animations)
- `@tailwindcss/vite` ^4.1.14

### TD-2: Vite Dev Proxy for API Communication
**Decision:** Use Vite's built-in proxy to forward `/api/*` requests to FastAPI during development.
**Rationale:**
- Avoids CORS issues during local development
- Single origin in the browser (port 3000)
- No hardcoded URLs in frontend code
- Production deployment uses reverse proxy (nginx) for same behavior

**Configuration:**
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/crawl': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### TD-3: SQLite for Application State Persistence
**Decision:** Add SQLite (via `aiosqlite` + raw SQL or `SQLModel`) for storing tasks, projects, settings, and user sessions.
**Rationale:**
- Zero-dependency database (no PostgreSQL needed for the QA agent itself)
- File-based, easy to backup and version alongside the project
- Sufficient for single-user/small-team workloads (< 100 concurrent users)
- ChromaDB remains for vector storage; SQLite handles relational CRUD
- Aligns with the project's principle of minimal infrastructure

**Schema (core tables):**
```sql
-- Projects
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    subtitle TEXT,
    environment TEXT DEFAULT 'Production',
    visibility TEXT DEFAULT 'Public',
    status TEXT DEFAULT 'ACTIVE',
    health_score INTEGER DEFAULT 100,
    integrations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks (Kanban items)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    business_group TEXT,
    priority TEXT DEFAULT 'MEDIUM',
    column_name TEXT DEFAULT 'TO DO',
    project_id TEXT REFERENCES projects(id),
    due_date TEXT,
    tags JSON,
    plane_task_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test Suites
CREATE TABLE test_suites (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    project_id TEXT REFERENCES projects(id),
    status TEXT DEFAULT 'PENDING',
    last_run TIMESTAMP,
    duration TEXT,
    executor TEXT,
    pass_rate REAL DEFAULT 0,
    steps JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Stories
CREATE TABLE stories (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    format TEXT DEFAULT 'markdown',
    epic TEXT,
    feature TEXT,
    target_role TEXT,
    is_indexed BOOLEAN DEFAULT FALSE,
    test_scenarios_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settings (key-value)
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (simple auth)
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'QA Engineer',
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Events (audit log)
CREATE TABLE system_events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    event_type TEXT DEFAULT 'info',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### TD-4: JWT-based Authentication
**Decision:** Implement simple JWT authentication with httpOnly cookies.
**Rationale:**
- Stateless token validation (no session store needed)
- httpOnly cookies prevent XSS token theft
- Short-lived access tokens (1 hour) + long-lived refresh (7 days)
- Simple enough for a team tool without enterprise SSO requirements

**Implementation:**
- Library: `python-jose[cryptography]` for JWT + `passlib[bcrypt]` for password hashing
- Login: `POST /api/auth/login` → returns httpOnly cookie with JWT
- Validation: middleware extracts JWT from cookie, validates, injects user into request
- Protected routes: all `/api/*` except `/api/auth/login` require valid token

### TD-5: Typed API Client Layer
**Decision:** Create a centralized API client in the frontend with TypeScript interfaces matching backend schemas.
**Rationale:**
- Single place to handle auth headers, error responses, and retries
- TypeScript interfaces ensure frontend/backend contract consistency
- Easy to mock for testing and storybook development
- Fetch-based (no axios dependency) for minimal bundle size

**Pattern:**
```typescript
// src/frontend/services/apiClient.ts
class ApiClient {
  private baseUrl = '/api';

  async get<T>(path: string): Promise<T> { ... }
  async post<T>(path: string, body: unknown): Promise<T> { ... }
  async patch<T>(path: string, body: unknown): Promise<T> { ... }
  async delete(path: string): Promise<void> { ... }
}

export const api = new ApiClient();
```

### TD-6: Real-time Status via Polling (Phase 1) → SSE (Phase 2)
**Decision:** Start with polling (5s interval) for live status updates, migrate to Server-Sent Events later.
**Rationale:**
- Polling is simple, works everywhere, and sufficient for small teams
- SSE (phase 2) provides true push updates without WebSocket complexity
- FastAPI supports SSE natively via `StreamingResponse`
- Frontend can switch from polling to EventSource with minimal refactoring

**Polling targets:**
- `GET /api/test-suites` (suite status changes)
- `GET /api/stats/overview` (dashboard metrics)
- `GET /api/tasks` (Kanban board state when Plane.so syncs)

### TD-7: Frontend Served via FastAPI Static Files (Production)
**Decision:** In production, serve the built frontend as static files from FastAPI.
**Rationale:**
- Single deployment artifact (one Docker container serves everything)
- No separate nginx needed for simple deployments
- `vite build` produces static assets in `frontend/dist/`
- FastAPI mounts `/` to serve `index.html` with SPA fallback
- API routes take precedence via path ordering

**Production serving:**
```python
# In src/api/app.py (production mode)
from fastapi.staticfiles import StaticFiles

if settings.environment == "production":
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

### TD-8: Docker Multi-Stage Build for Frontend
**Decision:** Use multi-stage Docker build: Node stage builds frontend, Python stage serves it.
**Rationale:**
- No Node.js in production image (smaller image)
- Build-time only dependency on npm/bun
- Final image contains only Python + static assets
- Consistent with existing Docker setup

```dockerfile
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/bun.lock ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Python app + built frontend
FROM python:3.11-slim
WORKDIR /app
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### TD-9: State Management — React Context + Hooks (No Redux)
**Decision:** Keep the existing React Context + custom hooks pattern from TestOps Pro.
**Rationale:**
- Already implemented and working in TestOps Pro
- Application state is moderate (not thousands of items)
- Context splits by concern (AppContext, ThemeContext) avoid re-render issues
- No additional library overhead (Redux, Zustand)
- Easy to refactor: replace `useState` with `useSWR` or `useQuery` for server state

**Migration strategy:**
- Replace `useState` with `useEffect` + `fetch()` for data that comes from the API
- Keep local UI state (modals, filters, view mode) in context as-is
- Add loading/error states to each data-fetching hook

### TD-10: Database Migrations via Simple Python Scripts
**Decision:** Use versioned SQL migration scripts rather than an ORM migration tool.
**Rationale:**
- Project uses raw SQL / simple queries — no heavy ORM
- Migration scripts are transparent and version-controlled
- Simple `scripts/migrate.py` applies pending `.sql` files in order
- Suitable for a tool with infrequent schema changes

**Migration naming:** `001_initial_schema.sql`, `002_add_stories_table.sql`, etc.

## Data Flows

### Flow 1: Dashboard Load
```
1. User opens frontend → Login (JWT cookie set)
2. Frontend calls GET /api/stats/overview
3. Backend queries SQLite: count tests, group by status, calculate velocity
4. Backend queries Allure results dir for recent execution data
5. Returns aggregated JSON → Frontend renders dashboard cards + charts
```

### Flow 2: Task CRUD (Kanban)
```
1. User creates/moves/deletes task in Kanban UI
2. Frontend calls POST/PATCH/DELETE /api/tasks
3. Backend persists to SQLite tasks table
4. If Plane.so configured: backend syncs change to Plane.so API (async)
5. Backend returns updated task → Frontend updates context state
```

### Flow 3: Test Suite Execution from UI
```
1. User clicks "Run" on a test suite
2. Frontend calls POST /api/test-suites/{id}/run
3. Backend updates suite status to RUNNING in SQLite
4. Backend spawns pytest subprocess (same as webhook flow)
5. Frontend polls GET /api/test-suites/{id} every 3s
6. pytest completes → Backend updates status to PASS/FAIL
7. Frontend receives updated status → Updates UI
8. If PASS + git enabled: auto-commit triggered
```

### Flow 4: User Story Upload & RAG Indexing
```
1. User fills story form (title, content, metadata) in UI
2. Frontend calls POST /api/stories with story data
3. Backend persists story to SQLite (is_indexed = false)
4. Backend triggers RAG pipeline: parse → chunk → embed → ChromaDB
5. Backend updates story (is_indexed = true, test_scenarios_count)
6. Frontend refreshes story list showing indexed status
```

### Flow 5: Site Crawl from UI
```
1. User fills crawl form (URL, max_depth, max_pages, generate_tests)
2. Frontend calls POST /crawl (existing endpoint)
3. Backend runs Playwright crawler (existing logic)
4. Frontend polls crawl status or waits for completion response
5. On completion: frontend fetches generated test files list
6. User reviews generated POM classes and test scripts in UI
```

## Security Considerations

- JWT tokens stored in httpOnly cookies (not localStorage)
- CSRF protection via SameSite=Strict cookie attribute
- Password hashing with bcrypt (cost factor 12)
- API rate limiting on auth endpoints (5 attempts per minute)
- Input validation on all form submissions (Pydantic on backend, TypeScript on frontend)
- SQLite database file permissions restricted (600)
- Frontend never exposes raw API keys — masked display with copy button
- CORS configured to allow only the frontend origin
- All backend query parameters sanitized to prevent SQL injection

## Error Handling Strategy

### Frontend Errors
- **Network failures:** Show toast notification, allow retry
- **401 Unauthorized:** Redirect to login screen, clear stale session
- **422 Validation:** Display field-level error messages from backend
- **500 Server Error:** Show generic error with "Contact admin" message
- **Loading states:** Skeleton loaders for all data-dependent views

### Backend Errors (New Endpoints)
- **Database errors:** Return 500 with structured error JSON, log full traceback
- **Plane.so sync failures:** Log warning, continue (non-blocking)
- **Test execution failures:** Update suite status to FAIL, capture stderr
- **Story indexing failures:** Mark story as is_indexed=false, return error details
- **Auth failures:** Return 401 with clear message, no information leakage

## Migration Strategy (Mock → Real Data)

The TestOps Pro frontend currently uses mock data in `src/data/mockData.ts` and `AppContext.tsx`. The migration follows this pattern:

1. **Create API client layer** — new `services/` directory with typed fetch functions
2. **Create custom hooks** — `useProjects()`, `useTasks()`, `useTestSuites()`, etc.
3. **Replace context state** — swap `useState(initialMockData)` with API-backed hooks
4. **Add loading/error UI** — skeleton states and error boundaries
5. **Remove mock data** — delete `mockData.ts` once all views use real API
6. **Keep context for UI state** — filters, view mode, theme remain in context
