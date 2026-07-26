"""Embedding provider abstraction layer.

Provides a unified interface for generating text embeddings using either
a local Ollama instance or the Google Generative AI API. Supports
transparent fallback from local to cloud.

Usage:
    from src.rag.embeddings import get_embedding_function

    embeddings = get_embedding_function(provider="ollama")
    vectors = embeddings.embed_documents(["text1", "text2"])
"""

from typing import Literal

from langchain_core.embeddings import Embeddings

from src.common.exceptions import EmbeddingError
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


def get_embedding_function(
    provider: Literal["ollama", "gemini"] | None = None,
) -> Embeddings:
    """Create and return an embedding function based on provider selection.

    Args:
        provider: Which embedding provider to use. If None, uses the
            configured LLM_PROVIDER from settings.

    Returns:
        A LangChain Embeddings instance.

    Raises:
        EmbeddingError: If the provider cannot be initialized.
    """
    settings = get_settings()
    selected_provider = provider or settings.llm_provider

    if selected_provider == "ollama":
        return _create_ollama_embeddings(settings)
    elif selected_provider == "gemini":
        return _create_gemini_embeddings(settings)
    else:
        raise EmbeddingError(
            model=selected_provider,
            reason=f"Unknown embedding provider: {selected_provider}",
        )


def _create_ollama_embeddings(settings) -> Embeddings:
    """Create Ollama embedding function for local inference.

    Uses the langchain_community OllamaEmbeddings wrapper.
    """
    try:
        from langchain_community.embeddings import OllamaEmbeddings

        logger.info(
            "initializing_ollama_embeddings",
            model=settings.ollama.embedding_model,
            base_url=settings.ollama.base_url,
        )

        return OllamaEmbeddings(
            model=settings.ollama.embedding_model,
            base_url=settings.ollama.base_url,
        )
    except ImportError as e:
        raise EmbeddingError(
            model="ollama",
            reason="langchain-community package not installed",
        ) from e
    except Exception as e:
        raise EmbeddingError(
            model=settings.ollama.embedding_model,
            reason=str(e),
        ) from e


def _create_gemini_embeddings(settings) -> Embeddings:
    """Create Google Generative AI embedding function for cloud inference.

    Requires a valid GEMINI_API_KEY in environment.
    """
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        if not settings.gemini.api_key:
            raise EmbeddingError(
                model="gemini",
                reason="GEMINI_API_KEY not configured",
            )

        logger.info(
            "initializing_gemini_embeddings",
            model=settings.gemini.embedding_model,
        )

        return GoogleGenerativeAIEmbeddings(
            model=settings.gemini.embedding_model,
            google_api_key=settings.gemini.api_key,
        )
    except ImportError as e:
        raise EmbeddingError(
            model="gemini",
            reason="langchain-google-genai package not installed",
        ) from e
    except EmbeddingError:
        raise
    except Exception as e:
        raise EmbeddingError(
            model=settings.gemini.embedding_model,
            reason=str(e),
        ) from e


def get_embedding_with_fallback() -> Embeddings:
    """Get embedding function with automatic fallback.

    Tries the primary provider first; if it fails, falls back to the
    alternate provider. This ensures embedding generation is resilient
    to single-provider outages.

    Returns:
        A LangChain Embeddings instance from whichever provider succeeds.

    Raises:
        EmbeddingError: If both providers fail.
    """
    settings = get_settings()
    primary = settings.llm_provider
    fallback = "gemini" if primary == "ollama" else "ollama"

    try:
        return get_embedding_function(provider=primary)
    except EmbeddingError as primary_error:
        logger.warning(
            "embedding_primary_failed_trying_fallback",
            primary=primary,
            fallback=fallback,
            error=str(primary_error),
        )
        try:
            return get_embedding_function(provider=fallback)
        except EmbeddingError as fallback_error:
            raise EmbeddingError(
                model=f"{primary}+{fallback}",
                reason=(
                    f"Both providers failed. Primary ({primary}): {primary_error.message}. "
                    f"Fallback ({fallback}): {fallback_error.message}"
                ),
            ) from fallback_error
