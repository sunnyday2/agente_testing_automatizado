---
inclusion: fileMatch
fileMatchPattern: "**/frontend/**"
---

# Frontend Standards: React & TypeScript Conventions

## TypeScript Configuration

- Strict mode enabled (`strict: true` in `tsconfig.json`)
- `noUnusedLocals` and `noUnusedParameters` enforced
- `noUncheckedIndexedAccess` for safer array/object access
- Path alias `@/*` maps to `src/*` for clean imports
- All files must use `.tsx` for components, `.ts` for non-JSX modules

## Component Patterns

### File Structure
- One component per file, named export matching filename
- Component files use PascalCase: `TaskCard.tsx`, `KanbanBoard.tsx`
- Utility/hook files use camelCase: `usePolling.ts`, `formatters.ts`

### Component Signature
```tsx
interface ComponentProps {
  /** Documented prop */
  value: string;
  /** Optional callback */
  onChange?: (value: string) => void;
}

export function Component({ value, onChange }: ComponentProps) {
  return <div>{value}</div>;
}
```

### Patterns to Follow
- Prefer function components with hooks (no class components except ErrorBoundary)
- Use `interface` for component props, not `type`
- Destructure props in the function signature
- Return early for loading/error/empty states
- Colocate related state with `useState`, not in context

### Patterns to Avoid
- No `any` types — use `unknown` and narrow, or specific types
- No inline styles — use Tailwind utility classes
- No barrel exports (`index.ts`) — import directly from component files
- No `useEffect` for data that should be in a hook — use custom hooks
- No global state for server data — keep in hooks with polling

## Context Usage

Context is for cross-cutting UI concerns only:
- **ThemeContext**: Light/dark mode preference
- **AuthContext**: User session state, login/logout actions
- **AppContext**: Current view, sidebar state

Server data (tasks, projects, suites) lives in hooks, NOT context.

## Data Fetching Pattern

### Custom Hooks
Every API resource gets a hook that encapsulates:
1. State (data, isLoading, error)
2. Fetch function (called by usePolling)
3. CRUD mutations (optimistic where possible)
4. Refresh function

```tsx
export function useResource(): UseResourceReturn {
  const [data, setData] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const result = await resourceService.getAll();
      setData(result.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { refresh } = usePolling(fetchData, {
    interval: POLLING_INTERVALS.NORMAL,
    enabled: true,
  });

  return { data, isLoading, error, refresh };
}
```

### Optimistic Updates
For move/delete operations:
1. Update local state immediately
2. Call API in background
3. Revert local state on failure (call `refresh()`)

## API Client

- All API calls go through `services/apiClient.ts`
- Service modules wrap specific endpoints (one per resource)
- Use `api` instance for `/api/*` routes, `rawApi` for non-prefixed routes (`/crawl`, `/health`)
- Never call `fetch()` directly in components

## Styling Conventions

### Tailwind CSS
- Use utility classes exclusively — no custom CSS except in `index.css`
- Use CSS variables from the theme (e.g., `text-foreground`, `bg-card`, `border-border`)
- Responsive: mobile-first with `sm:`, `lg:` breakpoints
- Dark mode handled automatically via CSS variables + `.dark` class

### Color System
- `--color-primary` / `text-primary` — brand/accent color
- `--color-foreground` / `text-foreground` — main text
- `--color-muted-foreground` / `text-muted-foreground` — secondary text
- `--color-destructive` / `text-destructive` — errors, delete actions
- `--color-success` — green for passing/success states

### Component Sizing
- Cards: `rounded-lg border border-border bg-card p-4 shadow-sm`
- Buttons: `rounded-md px-4 py-2 text-sm font-medium`
- Inputs: `rounded-md border border-input bg-background px-3 py-2 text-sm`
- Badges: `rounded-full px-2 py-0.5 text-xs font-medium`

## Import Organization

```tsx
// React/library imports
import { useState, useCallback, type ReactNode } from "react";
import { Icon } from "lucide-react";

// Internal: context, hooks
import { useAuth } from "@/context/AuthContext";
import { useTasks } from "@/hooks/useTasks";

// Internal: components
import { Badge } from "@/components/shared/Badge";

// Internal: services, utils, types
import { tasksService } from "@/services/tasksService";
import { formatDate } from "@/utils/formatters";
import type { Task, TaskColumn } from "@/types";
```

## Accessibility

- All interactive elements have `aria-label` when no visible text
- Form inputs have associated `<label>` elements with `htmlFor`
- Error messages use `role="alert"`
- Modals use `role="dialog"` and `aria-modal="true"`
- Keyboard navigation: Escape closes modals, Tab navigates form fields
- Color contrast: semantic colors meet WCAG AA standards

## Error Handling

- Network failures: Show error state in the hook consumer
- 401 responses: AuthContext redirects to login
- Form validation: Client-side before submission, server errors displayed inline
- Component crashes: ErrorBoundary catches and shows retry UI
- Loading states: Skeleton placeholders for all data-dependent views

## Testing Expectations

- TypeScript strict mode is the primary "test" — if it compiles, types are correct
- `npm run lint` (tsc --noEmit) must pass before any commit
- `npm run build` must produce zero errors
- No runtime `any` casts or `@ts-ignore` comments
