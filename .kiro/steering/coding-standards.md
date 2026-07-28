---
inclusion: auto
---

# Python & FastAPI Coding Standards

## General Python Conventions

- Use Python 3.11+ features (type hints, match statements, TypedDict)
- Follow PEP 8 style guide strictly
- Maximum line length: 100 characters
- Use `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- All functions and methods MUST have type annotations for parameters and return values
- Use `dataclasses` or `pydantic.BaseModel` for structured data, never raw dicts
- Prefer composition over inheritance
- Use `pathlib.Path` over `os.path` for file operations

## Import Organization

```python
# Standard library
import asyncio
from pathlib import Path

# Third-party
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import chromadb

# Local
from src.config.settings import settings
from src.rag.retriever import StoryRetriever
```

## FastAPI Patterns

- Use dependency injection via `Depends()` for services and configuration
- Define request/response models in `schemas/` using Pydantic v2
- Use `BackgroundTasks` for fire-and-forget operations (test execution)
- Always return structured JSON responses with consistent envelope:
  ```python
  {"status": "success|error", "data": {...}, "message": "..."}
  ```
- Use HTTPException with meaningful status codes and detail messages
- Add OpenAPI metadata (tags, summary, description) to all endpoints

## Async Patterns

- Use `async def` for all route handlers and service methods that do I/O
- Use `asyncio.create_subprocess_exec` for launching external processes
- Use `asyncio.gather` for parallel operations with proper error handling
- Never use `time.sleep()` — use `asyncio.sleep()` instead
- Use `asyncio.Semaphore` to limit concurrent test executions

## Error Handling

- Define custom exceptions in `src/common/exceptions.py`
- Use structured logging with context (request_id, task_id)
- Never catch bare `Exception` — always catch specific exception types
- Log errors at the boundary, not deep in business logic
- Return appropriate HTTP status codes (400 for bad input, 500 for internal errors, 202 for accepted async work)

## Configuration

- Use `pydantic_settings.BaseSettings` for all configuration
- Load from environment variables with `.env` file support
- Never hardcode URLs, API keys, or file paths
- Use reasonable defaults for development, require explicit values for production
- Group related settings into nested models

## Documentation

- All public functions must have docstrings (Google style)
- Complex algorithms need inline comments explaining "why", not "what"
- Keep README.md updated with setup instructions and API examples
