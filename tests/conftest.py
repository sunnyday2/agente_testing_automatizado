"""Shared test configuration and fixtures.

Provides common setup for all test types (unit, integration, e2e).
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure project root is in path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment variables before anything imports settings
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("PLANE_API_KEY", "")
os.environ.setdefault("PLANE_WEBHOOK_SECRET", "")
os.environ.setdefault("GIT_MODE", "disabled")
