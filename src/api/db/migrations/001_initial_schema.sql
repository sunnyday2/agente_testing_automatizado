-- Migration: 001_initial_schema.sql
-- Description: Create core application tables for TestOps Pro
-- Created: 2026-07-28

-- ============================================================
-- Users (authentication)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'QA Engineer',
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- ============================================================
-- Projects
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
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

CREATE INDEX idx_projects_status ON projects(status);

-- ============================================================
-- Tasks (Kanban board items)
-- ============================================================
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    business_group TEXT,
    priority TEXT DEFAULT 'MEDIUM',
    column_name TEXT DEFAULT 'TO DO',
    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
    due_date TEXT,
    tags JSON,
    plane_task_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_column ON tasks(column_name);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- ============================================================
-- Test Suites
-- ============================================================
CREATE TABLE IF NOT EXISTS test_suites (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'PENDING',
    last_run TIMESTAMP,
    duration TEXT,
    executor TEXT,
    pass_rate REAL DEFAULT 0,
    steps JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_suites_status ON test_suites(status);
CREATE INDEX idx_test_suites_project ON test_suites(project_id);

-- ============================================================
-- User Stories
-- ============================================================
CREATE TABLE IF NOT EXISTS stories (
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

CREATE INDEX idx_stories_indexed ON stories(is_indexed);
CREATE INDEX idx_stories_epic ON stories(epic);

-- ============================================================
-- Settings (key-value store)
-- ============================================================
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- System Events (audit log / activity feed)
-- ============================================================
CREATE TABLE IF NOT EXISTS system_events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    event_type TEXT DEFAULT 'info',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_events_type ON system_events(event_type);
CREATE INDEX idx_system_events_timestamp ON system_events(timestamp DESC);
