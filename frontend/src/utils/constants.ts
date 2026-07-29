import type { ColumnType, CategoryTag } from '@/types';

/** Kanban board column definitions */
export const KANBAN_COLUMNS: { id: ColumnType; title: string; colorClass: string }[] = [
  { id: 'IDEAS / PLANNING', title: 'IDEAS / PLANNING', colorClass: 'border-t-[var(--color-okra)]' },
  { id: 'BACKLOG', title: 'BACKLOG', colorClass: 'border-t-[var(--text-muted)]' },
  { id: 'TO DO', title: 'TO DO', colorClass: 'border-t-[var(--color-orange)]' },
  { id: 'IN PROGRESS', title: 'IN PROGRESS', colorClass: 'border-t-[var(--color-matcha)]' },
  { id: 'REVIEW / TESTING', title: 'REVIEW / TESTING', colorClass: 'border-t-[var(--color-brown)]' },
  { id: 'DONE', title: 'DONE', colorClass: 'border-t-[var(--color-light-green)]' },
];

/** Business/category tag filter options */
export const CATEGORY_TAGS: CategoryTag[] = [
  'ALL',
  'AI Native Business',
  'AI Professionals Network',
  'Practical AI For Business',
  'AI Book Coach',
  'The Mum Project',
  'The Bridge Podcast',
  'Operations',
  'Other',
];

/** Test suite filter categories */
export const TEST_SUITE_CATEGORIES = [
  'ALL',
  'E2E Validation',
  'API Security',
  'Infrastructure',
  'Performance',
] as const;

/** Environment options for projects */
export const ENVIRONMENTS = ['Production', 'Staging', 'Dev'] as const;

/** Priority levels with badge classes */
export const PRIORITY_BADGE_CLASSES = {
  HIGH: 'badge-dark-red',
  MEDIUM: 'badge-orange',
  LOW: 'badge-matcha',
} as const;
