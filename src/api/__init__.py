"""FastAPI application package.

Contains the app factory, route handlers, schemas, services,
and middleware for the QA Automation Agent API.
"""

from src.api.app import create_app

__all__ = ["create_app"]
