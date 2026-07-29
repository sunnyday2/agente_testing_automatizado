# TestOps Pro Frontend

React + TypeScript + Vite frontend for the QA Automation Agent dashboard.

## Tech Stack

- **React 19** — UI framework with concurrent features
- **TypeScript 5.8** — Strict mode for type safety
- **Vite 6** — Build tool with HMR
- **Tailwind CSS 4** — Utility-first styling with CSS variables
- **Recharts 3** — Chart library (velocity, pie, bar)
- **Lucide React** — Icon library
- **Motion** — Animation library

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:3000. The Vite dev server proxies `/api/*` to the backend on port 8000.

**Default login:** `admin@testops.local` / `admin123`

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server (port 3000, HMR) |
| `npm run build` | TypeScript check + production build |
| `npm run lint` | TypeScript type checking only |
| `npm run preview` | Preview production build |

## Architecture

```
src/
├── App.tsx                    # Root: providers → auth gate → view router
├── main.tsx                   # React DOM entry point
├── index.css                  # Tailwind + CSS variables (light/dark themes)
├── types.ts                   # Shared TypeScript interfaces (295 lines)
│
├── context/                   # React Context providers
│   ├── ThemeContext.tsx        # Light/dark mode (localStorage + system pref)
│   ├── AuthContext.tsx         # Login/logout/session management
│   └── AppContext.tsx          # UI state (currentView, sidebar toggle)
│
├── components/
│   ├── layout/                # Shell layout
│   │   ├── AppShell.tsx       # Header + Sidebar + main content area
│   │   ├── Header.tsx         # Logo, theme toggle, user info, logout
│   │   └── Sidebar.tsx        # 8 nav items with active state
│   │
│   ├── auth/
│   │   └── LoginScreen.tsx    # Email/password form with validation
│   │
│   ├── dashboard/             # Overview view
│   │   ├── OverviewDashboard.tsx  # Main: stat cards + stream + events
│   │   ├── StatCard.tsx           # Reusable metric card
│   │   ├── ProjectCard.tsx        # Health score bar + badges
│   │   ├── SystemEventsFeed.tsx   # Activity feed with type icons
│   │   └── TestStreamTable.tsx    # Live suites table (self-polling)
│   │
│   ├── kanban/                # Kanban board view
│   │   ├── KanbanBoard.tsx    # Main: columns + CRUD + drag-drop
│   │   ├── KanbanColumn.tsx   # Drop target with task list
│   │   ├── TaskCard.tsx       # Draggable card with action menu
│   │   ├── TaskModal.tsx      # Create/edit form modal
│   │   └── KanbanFilters.tsx  # Category/priority filters
│   │
│   ├── tests/                 # Test suites view
│   │   ├── TestSuites.tsx     # Split: list left, console right
│   │   ├── SuiteListItem.tsx  # Status dot, name, pass rate
│   │   ├── SuiteConsole.tsx   # Run button + steps display
│   │   └── StepRow.tsx        # Status icon + error message
│   │
│   ├── reports/               # Analytics view
│   │   ├── ExecutionReports.tsx   # Date filter + charts grid
│   │   ├── VelocityChart.tsx      # Area chart (recharts)
│   │   ├── FailurePieChart.tsx    # Donut pie chart
│   │   └── PassRateChart.tsx      # Bar chart with colored cells
│   │
│   ├── projects/              # Projects view
│   │   ├── AllProjects.tsx    # Grid + create modal
│   │   ├── CreateProject.tsx  # Modal form
│   │   └── ProjectDetailCard.tsx  # Health bar + actions
│   │
│   ├── stories/               # User stories view
│   │   ├── StoriesPage.tsx    # Grid + upload form + seed
│   │   ├── StoryCard.tsx      # Indexed indicator + metadata
│   │   ├── StoryUploadForm.tsx    # MD/JSON format toggle
│   │   └── StoryDetailModal.tsx   # Full content viewer
│   │
│   ├── crawl/                 # Site crawl view
│   │   ├── CrawlPage.tsx     # Form + progress/results
│   │   ├── CrawlForm.tsx     # URL, depth slider, options
│   │   ├── CrawlProgress.tsx # Elapsed timer + animation
│   │   └── CrawlResults.tsx  # Stats, pages, generated files
│   │
│   ├── settings/              # Settings view
│   │   ├── SettingsPage.tsx   # Main layout
│   │   ├── ThemeSettings.tsx  # Light/dark toggle cards
│   │   ├── WebhookSettings.tsx    # URL + notification toggles
│   │   └── ApiKeySettings.tsx     # Masked keys + copy
│   │
│   └── shared/                # Reusable UI components
│       ├── Badge.tsx          # 6 color variants + dot
│       ├── Modal.tsx          # Overlay with escape/click-outside
│       ├── Toast.tsx          # ToastProvider + useToast hook
│       ├── LoadingSkeleton.tsx    # Pulse animation variants
│       ├── ErrorBoundary.tsx  # React error boundary + retry
│       └── EmptyState.tsx     # Empty list placeholder
│
├── hooks/                     # Data-fetching hooks
│   ├── usePolling.ts          # Generic interval polling
│   ├── useStats.ts            # Dashboard overview (5s poll)
│   ├── useTasks.ts            # Kanban CRUD + optimistic updates
│   ├── useTestSuites.ts       # Suite list + run (3s when running)
│   ├── useReports.ts          # Analytics data (15s poll)
│   ├── useProjects.ts         # Project CRUD (15s poll)
│   ├── useStories.ts          # Story CRUD + seed (15s poll)
│   └── useSettings.ts         # Settings read/write
│
├── services/                  # API client layer
│   ├── apiClient.ts           # Base fetch wrapper (GET/POST/PATCH/DELETE)
│   ├── authService.ts         # Login, logout, getMe
│   ├── tasksService.ts        # Tasks CRUD + move
│   ├── testSuitesService.ts   # Suites list + run
│   ├── reportsService.ts      # Stats, velocity, failures, analytics
│   ├── projectsService.ts     # Projects CRUD
│   ├── storiesService.ts      # Stories CRUD + seed
│   ├── crawlService.ts        # Trigger crawl
│   └── settingsService.ts     # Settings read/write
│
└── utils/
    ├── formatters.ts          # Date, duration, number, percent, file size
    └── constants.ts           # Columns, categories, priorities, statuses
```

## Design Patterns

### Context Hierarchy

```
ThemeProvider (light/dark)
  └── AuthProvider (session management)
        └── AuthGate (login screen vs app)
              └── AppProvider (UI state)
                    └── AppShell → ViewRouter
```

### Data Fetching

- All server data lives in **hooks** (not context)
- Hooks use `usePolling()` for automatic refresh
- Polling speeds up during active operations (e.g., 3s while test suite is RUNNING)
- Optimistic updates for move/delete operations (revert on failure)
- Loading skeletons shown during initial fetch

### API Client

- Single `apiClient.ts` with typed `get<T>`, `post<T>`, `patch<T>`, `delete<T>`
- Credentials included via `credentials: "include"` (httpOnly cookies)
- 401 responses dispatch `auth:unauthorized` event
- Service modules wrap specific endpoint groups

### Styling

- Tailwind CSS 4 with CSS custom properties for theming
- Dark mode via `.dark` class on `<html>` (persisted in localStorage)
- No component library — all custom components
- Responsive: mobile-first with `sm:`, `lg:` breakpoints

## Production Bundle

- **JS**: ~207 KB gzipped
- **CSS**: ~7.4 KB gzipped
- **Total**: ~215 KB gzipped (well under 500KB target)
- Build time: ~12s
