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

    Initializes logging and any required services on startup,
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

    yield

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


def _register_routes(app: FastAPI) -> None:
    """Register all API route modules.

    Args:
        app: The FastAPI application.
    """
    from src.api.routes.crawl import router as crawl_router
    from src.api.routes.health import router as health_router
    from src.api.routes.reports import router as reports_router
    from src.api.routes.webhooks import router as webhooks_router

    app.include_router(health_router, tags=["Health"])
    app.include_router(webhooks_router, tags=["Webhooks"])
    app.include_router(crawl_router, tags=["Crawl"])
    app.include_router(reports_router, tags=["Reports"])


# Module-level app instance for uvicorn
app = create_app()
