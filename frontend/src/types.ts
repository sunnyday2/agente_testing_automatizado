export type AppView = 
  | 'overview' 
  | 'boards' 
  | 'projects' 
  | 'create-project' 
  | 'tests' 
  | 'reports' 
  | 'login' 
  | 'settings';

export type Priority = 'HIGH' | 'MEDIUM' | 'LOW';

export type ColumnType = 
  | 'IDEAS / PLANNING' 
  | 'BACKLOG' 
  | 'TO DO' 
  | 'IN PROGRESS' 
  | 'REVIEW / TESTING' 
  | 'DONE';

export type CategoryTag = 
  | 'ALL' 
  | 'AI Native Business' 
  | 'AI Professionals Network' 
  | 'Practical AI For Business' 
  | 'AI Book Coach' 
  | 'The Mum Project' 
  | 'The Bridge Podcast' 
  | 'Operations' 
  | 'Other';

export type ViewMode = 'Dashboard' | 'Board' | 'Swim Lanes' | 'Due Date' | 'Compact' | 'List';

export interface Assignee {
  id: string;
  name: string;
  role: string;
  avatar: string;
}

export interface TaskCard {
  id: string;
  title: string;
  description: string;
  category: string; // e.g. OPERATIONS, MOBILE-QA, API-TESTING, SECURITY, UI-AUTOMATION
  businessGroup: CategoryTag; // e.g. AI Native Business
  priority: Priority;
  column: ColumnType;
  dueDate?: string;
  assignees: Assignee[];
  tags: string[];
  testRunnerLink?: string;
  commentsCount?: number;
}

export interface Project {
  id: string;
  name: string;
  subtitle: string;
  healthScore: number;
  status: 'ACTIVE' | 'QUEUE' | 'CRITICAL' | 'COMPLETED';
  environment: 'Production' | 'Staging' | 'Dev';
  visibility: 'Public' | 'Private';
  totalSuites: number;
  openIssues: number;
  lastRun: string;
  members: Assignee[];
  integrations: {
    jenkins: boolean;
    slack: boolean;
    jira: boolean;
    s3: boolean;
  };
}

export interface TestStep {
  id: string;
  name: string;
  status: 'PASSED' | 'FAILED' | 'RUNNING' | 'SKIPPED';
  durationMs: number;
  logs?: string;
}

export interface TestSuite {
  id: string;
  name: string;
  category: string;
  project: string;
  status: 'PASS' | 'FAIL' | 'RUNNING' | 'PENDING';
  lastRun: string;
  duration: string;
  executor: string;
  passRate: number;
  steps: TestStep[];
}

export interface SystemEvent {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar: string;
  isAuthenticated: boolean;
}
