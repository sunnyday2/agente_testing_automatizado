"""Register generated test files as test suites in the database."""
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "qa_agent.db"

conn = sqlite3.connect(str(DB_PATH))

# Add test_path column if missing
try:
    conn.execute("SELECT test_path FROM test_suites LIMIT 1")
except sqlite3.OperationalError:
    conn.execute("ALTER TABLE test_suites ADD COLUMN test_path TEXT")
    conn.commit()
    print("Added test_path column")

# Clear existing suites to avoid duplicates
conn.execute("DELETE FROM test_suites")
conn.commit()

now = datetime.now(timezone.utc).isoformat()

suites = [
    {
        "id": f"suite_{uuid.uuid4().hex[:8]}",
        "name": "Smoke Tests - All Pages Load",
        "category": "E2E Validation",
        "status": "PENDING",
        "pass_rate": 0.0,
        "steps": "[]",
        "test_path": "tests/e2e/generated/tests/test_smoke_generated.py",
        "created_at": now,
    },
    {
        "id": f"suite_{uuid.uuid4().hex[:8]}",
        "name": "Navigation Tests - Page Connectivity",
        "category": "E2E Validation",
        "status": "PENDING",
        "pass_rate": 0.0,
        "steps": "[]",
        "test_path": "tests/e2e/generated/tests/test_navigation_generated.py",
        "created_at": now,
    },
    {
        "id": f"suite_{uuid.uuid4().hex[:8]}",
        "name": "Form Tests - Input Fields",
        "category": "E2E Validation",
        "status": "PENDING",
        "pass_rate": 0.0,
        "steps": "[]",
        "test_path": "tests/e2e/generated/tests/test_forms_generated.py",
        "created_at": now,
    },
    {
        "id": f"suite_{uuid.uuid4().hex[:8]}",
        "name": "Action Tests - Buttons & Interactions",
        "category": "E2E Validation",
        "status": "PENDING",
        "pass_rate": 0.0,
        "steps": "[]",
        "test_path": "tests/e2e/generated/tests/test_actions_generated.py",
        "created_at": now,
    },
]

for s in suites:
    conn.execute(
        """INSERT INTO test_suites (id, name, category, status, pass_rate, steps, test_path, created_at)
           VALUES (:id, :name, :category, :status, :pass_rate, :steps, :test_path, :created_at)""",
        s,
    )

conn.commit()

rows = conn.execute("SELECT id, name, status, test_path FROM test_suites").fetchall()
print(f"Registered {len(rows)} test suites:")
for r in rows:
    print(f"  [{r[2]}] {r[1]} → {r[3]}")

conn.close()
