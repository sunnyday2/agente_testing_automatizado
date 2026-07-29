"""FastAPI application factory.

Creates and configures the FastAPI app with middleware, CORS,
exception handlers, and route registration.

Usage:
    from src.api.app import create_app

    app = create_app()

    # Or run directly:
    # uvicorn src.api.app:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.common.exceptions import QAAgentError
from src.common.logging import get_logger, setup_logging
from src.config.settings import get_settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events.

    Initializes logging, database, and any required services on startup,
    and cleans up resources on shutdown.
    """
    settings = get_settings()

    # Initialize structured logging
    setup_logging(
        log_level=settings.log_level,
        log_format=settings.log_format,
    )

    logger.info(
        "application_starting",
        environment=settings.environment,
        llm_provider=settings.llm_provider,
    )

    # Initialize database and run migrations
    from src.api.db.connection import close_db, init_db, run_migrations

    db_path = settings.database.path
    migrations_dir = settings.database.migrations_dir

    logger.info("database_initializing", db_path=db_path)
    await run_migrations(db_path, migrations_dir)
    await init_db(db_path)
    logger.info("database_ready")

    yield

    # Shutdown: close database connection
    await close_db()
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="QA Automation Agent",
        description=(
            "AI-powered QA Automation & Reporting Agent. "
            "Generates test scenarios from user stories and site crawling, "
            "executes Playwright tests, and produces Allure reports."
        ),
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.api.debug,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
    )

    # --- Middleware ---
    _configure_cors(app, settings)
    _configure_exception_handlers(app)

    # --- Routes ---
    _register_routes(app)

    # --- Static Frontend (Production) ---
    _configure_frontend_serving(app, settings)

    return app


def _configure_cors(app: FastAPI, settings) -> None:
    """Configure CORS middleware.

    Args:
        app: The FastAPI application.
        settings: Application settings with CORS origins.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _configure_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers.

    Args:
        app: The FastAPI application.
    """

    @app.exception_handler(QAAgentError)
    async def qa_agent_error_handler(request: Request, exc: QAAgentError) -> JSONResponse:
        """Handle all QA Agent custom exceptions."""
        logger.error(
            "request_error",
            error_type=type(exc).__name__,
            message=exc.message,
            details=exc.details,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=_error_to_status_code(exc),
            content={
                "error": type(exc).__name__,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(
            "unhandled_exception",
            error_type=type(exc).__name__,
            message=str(exc),
            path=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": {},
            },
        )


def _error_to_status_code(exc: QAAgentError) -> int:
    """Map custom exceptions to HTTP status codes.

    Args:
        exc: The QA Agent exception.

    Returns:
        Appropriate HTTP status code.
    """
    from src.common.exceptions import (
        ConfigurationError,
        CrawlerError,
        IntegrationError,
        PlaneAPIError,
        WebhookValidationError,
    )

    if isinstance(exc, WebhookValidationError):
        return 401
    if isinstance(exc, ConfigurationError):
        return 500
    if isinstance(exc, PlaneAPIError):
        return 502
    if isinstance(exc, IntegrationError):
        return 502
    if isinstance(exc, CrawlerError):
        return 422
    return 500


def _configure_frontend_serving(app: FastAPI, settings) -> None:
    """Serve built frontend in production mode with SPA fallback.

    In production, mounts frontend/dist/ as static files and serves
    index.html for all non-API routes (SPA fallback).

    Args:
        app: The FastAPI application.
        settings: Application settings.
    """
    from pathlib import Path

    if settings.environment != "production":
        return

    frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if not frontend_dist.exists():
        logger.warning("frontend_dist_not_found", path=str(frontend_dist))
        return

    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    # SPA fallback: serve index.html for non-API, non-static routes
    index_html = frontend_dist / "index.html"

    @app.middleware("http")
    async def spa_fallback(request, call_next):
        """Serve index.html for frontend routes (SPA fallback)."""
        response = await call_next(request)
        # If 404 and not an API/static route, serve index.html
        if response.status_code == 404:
            path = request.url.path
            if not path.startswith(("/api", "/health", "/crawl", "/webhooks", "/reports", "/docs", "/redoc", "/openapi")):
                if index_html.exists():
                    return FileResponse(str(index_html))
        return response

    # Mount static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="static-assets")

    # Mount root static files (favicon, etc.)
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    logger.info("frontend_serving_enabled", path=str(frontend_dist))


def _register_routes(app: FastAPI) -> None:
    """Register all API route modules.

    Args:
        app: The FastAPI application.
    """
    from src.api.routes.auth import router as auth_router
    from src.api.routes.crawl import router as crawl_router
    from src.api.routes.health import router as health_router
    from src.api.routes.projects import router as projects_router
    from src.api.routes.reports import router as reports_router
    from src.api.routes.settings import router as settings_router
    from src.api.routes.stats import analytics_router, router as stats_router
    from src.api.routes.stories import router as stories_router
    from src.api.routes.tasks import router as tasks_router
    from src.api.routes.test_suites import router as test_suites_router
    from src.api.routes.webhooks import router as webhooks_router

    app.include_router(health_router, tags=["Health"])
    app.include_router(auth_router, tags=["Authentication"])
    app.include_router(projects_router, tags=["Projects"])
    app.include_router(tasks_router, tags=["Tasks"])
    app.include_router(test_suites_router, tags=["Test Suites"])
    app.include_router(stories_router, tags=["Stories"])
    app.include_router(stats_router, tags=["Stats"])
    app.include_router(settings_router, tags=["Settings"])
    app.include_router(analytics_router, tags=["Reports"])
    app.include_router(webhooks_router, tags=["Webhooks"])
    app.include_router(crawl_router, tags=["Crawl"])
    app.include_router(reports_router, tags=["Reports"])


# Module-level app instance for uvicorn
app = create_app()
