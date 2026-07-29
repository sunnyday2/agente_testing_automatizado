-- Migration: 002_seed_default_data.sql
-- Description: Seed default admin user and sample project
-- Created: 2026-07-28
--
-- Default admin credentials:
--   Email: admin@testops.local
--   Password: admin123 (bcrypt hash below)
--
-- NOTE: Change the password immediately in production!

-- ============================================================
-- Default admin user
-- Password: admin123 (bcrypt hash with cost factor 12)
-- ============================================================
INSERT OR IGNORE INTO users (id, email, name, role, hashed_password)
VALUES (
    'usr_default_admin_001',
    'admin@testops.local',
    'Admin',
    'Admin',
    '$2b$12$GnVIAUgTvYGw/13Ooxilt.GIfJpVj03L2R3h2SJA0PdZ/jAkFsrxC'
);

-- ============================================================
-- Sample project
-- ============================================================
INSERT OR IGNORE INTO projects (id, name, subtitle, environment, visibility, status, health_score)
VALUES (
    'proj_sample_001',
    'Sample E-Commerce App',
    'Demo project for QA automation testing',
    'Production',
    'Public',
    'ACTIVE',
    85
);

-- ============================================================
-- Default application settings
-- ============================================================
INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'dark');
INSERT OR IGNORE INTO settings (key, value) VALUES ('notifications_enabled', 'true');
INSERT OR IGNORE INTO settings (key, value) VALUES ('auto_run_tests', 'false');
INSERT OR IGNORE INTO settings (key, value) VALUES ('webhook_url', '');
INSERT OR IGNORE INTO settings (key, value) VALUES ('email_alerts', 'false');
INSERT OR IGNORE INTO settings (key, value) VALUES ('alert_on_failure', 'true');

-- ============================================================
-- Initial system event
-- ============================================================
INSERT OR IGNORE INTO system_events (id, title, description, event_type)
VALUES (
    'evt_system_init_001',
    'System Initialized',
    'TestOps Pro database created and seeded with default data.',
    'info'
);
