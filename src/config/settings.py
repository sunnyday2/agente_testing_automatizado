"""Application settings using Pydantic BaseSettings.

Loads configuration from environment variables and .env file.
All settings are validated at startup to fail fast on misconfiguration.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class OllamaSettings(BaseSettings):
    """Ollama local LLM configuration."""

    model_config = SettingsConfigDict(env_prefix="OLLAMA_")

    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    embedding_model: str = "qwen2.5:7b"
    timeout: int = 120
    max_retries: int = 3


class GeminiSettings(BaseSettings):
    """Google Gemini API configuration."""

    model_config = SettingsConfigDict(env_prefix="GEMINI_")

    api_key: str = ""
    model: str = "gemini-2.5-flash"
    embedding_model: str = "models/embedding-001"
    max_retries: int = 3


class ChromaDBSettings(BaseSettings):
    """ChromaDB vector store configuration."""

    model_config = SettingsConfigDict(env_prefix="CHROMA_")

    persist_directory: str = str(PROJECT_ROOT / "data" / "chroma")
    collection_name: str = "user_stories_v1"
    distance_function: str = "cosine"


class RAGSettings(BaseSettings):
    """RAG pipeline configuration."""

    model_config = SettingsConfigDict(env_prefix="RAG_")

    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    similarity_threshold: float = 0.7
    stories_directory: str = str(PROJECT_ROOT / "data" / "stories")


class PlaneSettings(BaseSettings):
    """Plane.so integration configuration."""

    model_config = SettingsConfigDict(env_prefix="PLANE_")

    base_url: str = "http://localhost:8080"
    api_key: str = ""
    workspace_slug: str = ""
    project_id: str = ""
    webhook_secret: str = ""


class CrawlerSettings(BaseSettings):
    """Site crawler configuration."""

    model_config = SettingsConfigDict(env_prefix="CRAWLER_")

    max_depth: int = 3
    max_pages: int = 50
    timeout_per_page: int = 10000  # milliseconds
    screenshot_pages: bool = True
    extract_elements: bool = True
    headless: bool = True
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"


class TestRunnerSettings(BaseSettings):
    """Test execution configuration."""

    model_config = SettingsConfigDict(env_prefix="TEST_")

    base_url: str = "http://localhost:3000"
    headless: bool = True
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    max_parallel: int = 3
    timeout: int = 30000  # milliseconds
    allure_results_dir: str = str(PROJECT_ROOT / "data" / "allure-results")
    retry_on_failure: bool = True
    max_retries: int = 1


class GitCommitSettings(BaseSettings):
    """Git auto-commit configuration for successful test runs."""

    model_config = SettingsConfigDict(env_prefix="GIT_")

    enabled: bool = True
    mode: Literal["commit-only", "commit-and-push", "disabled"] = "commit-only"
    remote: str = "origin"
    branch: str = ""  # Empty string = current branch
    stage_patterns: list[str] = [
        "tests/e2e/generated/**",
        "data/allure-results/**",
    ]
    commit_message_template: str = "test({feature}): PASSED - {timestamp} - {summary}"
    author_name: str = "QA Automation Agent"
    author_email: str = "qa-agent@automation.local"

    @field_validator("stage_patterns", mode="before")
    @classmethod
    def parse_stage_patterns(cls, v: str | list[str]) -> list[str]:
        """Parse stage patterns from comma-separated string or list."""
        if isinstance(v, str):
            return [p.strip() for p in v.split(",")]
        return v


class APISettings(BaseSettings):
    """FastAPI application configuration."""

    model_config = SettingsConfigDict(env_prefix="API_")

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    workers: int = 1

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class Settings(BaseSettings):
    """Root application settings aggregating all sub-configurations."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application metadata
    app_name: str = "QA Automation Agent"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "console"] = "console"

    # LLM provider preference
    llm_provider: Literal["ollama", "gemini"] = Field(
        default="ollama",
        description="Primary LLM provider. Falls back to the other on failure.",
    )

    # Sub-configurations
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    chromadb: ChromaDBSettings = Field(default_factory=ChromaDBSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    plane: PlaneSettings = Field(default_factory=PlaneSettings)
    crawler: CrawlerSettings = Field(default_factory=CrawlerSettings)
    test_runner: TestRunnerSettings = Field(default_factory=TestRunnerSettings)
    git: GitCommitSettings = Field(default_factory=GitCommitSettings)
    api: APISettings = Field(default_factory=APISettings)


def get_settings() -> Settings:
    """Create and return application settings instance.

    This function is intended to be used as a FastAPI dependency
    or called at application startup.
    """
    return Settings()
