"""Structured logging setup using structlog.

Provides JSON-formatted logs in production and human-readable colored
output in development. Integrates with Python's standard logging to
capture third-party library logs in the same format.

Usage:
    from src.common.logging import setup_logging, get_logger

    setup_logging(log_level="INFO", log_format="json")
    logger = get_logger(__name__)
    logger.info("server_started", port=8000)
"""

import logging
import sys
from typing import Literal

import structlog


def setup_logging(
    log_level: str = "INFO",
    log_format: Literal["json", "console"] = "console",
) -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Output format - "json" for production, "console" for development.
    """
    # Processors for structlog's own loggers
    structlog_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Processors used by ProcessorFormatter for stdlib logging
    stdlib_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )

    # Configure structlog for direct usage (structlog.get_logger())
    structlog.configure(
        processors=[
            *structlog_processors,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure Python's standard logging to route through structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=stdlib_processors,
    )

    # Root handler: send all logs to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Quiet down noisy third-party loggers
    for noisy_logger in ("httpx", "httpcore", "chromadb", "uvicorn.access"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        A bound structlog logger with structured output capabilities.
    """
    return structlog.get_logger(name)
