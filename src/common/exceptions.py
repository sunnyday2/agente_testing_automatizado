"""Custom exception hierarchy for the QA Automation Agent.

All application-specific exceptions inherit from QAAgentError,
allowing centralized error handling in the API layer.

Hierarchy:
    QAAgentError (base)
    ├── ConfigurationError
    ├── RAGError
    │   ├── DocumentLoadError
    │   ├── EmbeddingError
    │   └── RetrievalError
    ├── AgentError
    │   ├── LLMProviderError
    │   ├── LLMTimeoutError
    │   ├── LLMResponseParseError
    │   └── StateTransitionError
    ├── CrawlerError
    │   ├── NavigationError
    │   ├── ElementExtractionError
    │   └── CrawlDepthExceededError
    ├── TestExecutionError
    │   ├── TestRunnerError
    │   └── TestTimeoutError
    ├── IntegrationError
    │   ├── PlaneAPIError
    │   └── WebhookValidationError
    └── GitCommitError
"""


class QAAgentError(Exception):
    """Base exception for all QA Automation Agent errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# --- Configuration ---


class ConfigurationError(QAAgentError):
    """Raised when application configuration is invalid or missing."""


# --- RAG System ---


class RAGError(QAAgentError):
    """Base exception for RAG pipeline errors."""


class DocumentLoadError(RAGError):
    """Raised when a document cannot be loaded or parsed."""

    def __init__(self, file_path: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to load document: {file_path}",
            details={"file_path": file_path, "reason": reason},
        )


class EmbeddingError(RAGError):
    """Raised when embedding generation fails."""

    def __init__(self, model: str, reason: str) -> None:
        super().__init__(
            message=f"Embedding generation failed with model '{model}'",
            details={"model": model, "reason": reason},
        )


class RetrievalError(RAGError):
    """Raised when vector store retrieval fails."""

    def __init__(self, query: str, reason: str) -> None:
        super().__init__(
            message="Vector store retrieval failed",
            details={"query": query[:100], "reason": reason},
        )


# --- Agent / LLM ---


class AgentError(QAAgentError):
    """Base exception for LangGraph agent errors."""


class LLMProviderError(AgentError):
    """Raised when all LLM providers fail (primary + fallback)."""

    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(
            message=f"LLM provider '{provider}' failed",
            details={"provider": provider, "reason": reason},
        )


class LLMTimeoutError(AgentError):
    """Raised when an LLM call exceeds the configured timeout."""

    def __init__(self, provider: str, timeout_seconds: int) -> None:
        super().__init__(
            message=f"LLM call to '{provider}' timed out after {timeout_seconds}s",
            details={"provider": provider, "timeout_seconds": timeout_seconds},
        )


class LLMResponseParseError(AgentError):
    """Raised when the LLM response cannot be parsed into the expected schema."""

    def __init__(self, expected_schema: str, raw_response: str) -> None:
        super().__init__(
            message=f"Failed to parse LLM response into {expected_schema}",
            details={
                "expected_schema": expected_schema,
                "raw_response": raw_response[:500],
            },
        )


class StateTransitionError(AgentError):
    """Raised when an invalid state transition is attempted in the agent graph."""

    def __init__(self, from_state: str, to_state: str, reason: str) -> None:
        super().__init__(
            message=f"Invalid state transition: {from_state} -> {to_state}",
            details={"from_state": from_state, "to_state": to_state, "reason": reason},
        )


# --- Crawler ---


class CrawlerError(QAAgentError):
    """Base exception for site crawler errors."""


class NavigationError(CrawlerError):
    """Raised when the crawler cannot navigate to a page."""

    def __init__(self, url: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to navigate to: {url}",
            details={"url": url, "reason": reason},
        )


class ElementExtractionError(CrawlerError):
    """Raised when DOM element extraction fails on a page."""

    def __init__(self, url: str, reason: str) -> None:
        super().__init__(
            message=f"Element extraction failed on: {url}",
            details={"url": url, "reason": reason},
        )


class CrawlDepthExceededError(CrawlerError):
    """Raised when the crawler exceeds the configured maximum depth."""

    def __init__(self, max_depth: int, current_depth: int) -> None:
        super().__init__(
            message=f"Crawl depth exceeded: {current_depth} > {max_depth}",
            details={"max_depth": max_depth, "current_depth": current_depth},
        )


# --- Test Execution ---


class TestExecutionError(QAAgentError):
    """Base exception for test execution errors."""


class TestRunnerError(TestExecutionError):
    """Raised when the test runner subprocess fails."""

    def __init__(self, exit_code: int, stderr: str) -> None:
        super().__init__(
            message=f"Test runner exited with code {exit_code}",
            details={"exit_code": exit_code, "stderr": stderr[:1000]},
        )


class TestTimeoutError(TestExecutionError):
    """Raised when test execution exceeds the configured timeout."""

    def __init__(self, timeout_seconds: int, test_suite: str) -> None:
        super().__init__(
            message=f"Test suite '{test_suite}' timed out after {timeout_seconds}s",
            details={"timeout_seconds": timeout_seconds, "test_suite": test_suite},
        )


# --- Integration ---


class IntegrationError(QAAgentError):
    """Base exception for external service integration errors."""


class PlaneAPIError(IntegrationError):
    """Raised when Plane.so API calls fail."""

    def __init__(self, endpoint: str, status_code: int, response_body: str) -> None:
        super().__init__(
            message=f"Plane.so API error: {status_code} on {endpoint}",
            details={
                "endpoint": endpoint,
                "status_code": status_code,
                "response_body": response_body[:500],
            },
        )


class WebhookValidationError(IntegrationError):
    """Raised when webhook signature validation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message="Webhook signature validation failed",
            details={"reason": reason},
        )


# --- Git Operations ---


class GitCommitError(QAAgentError):
    """Raised when automatic Git commit operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        super().__init__(
            message=f"Git {operation} failed: {reason}",
            details={"operation": operation, "reason": reason},
        )
