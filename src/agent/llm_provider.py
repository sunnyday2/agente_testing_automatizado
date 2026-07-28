"""LLM provider abstraction with fallback and retry logic.

Provides a unified interface for calling local (Ollama) and cloud (Gemini)
LLMs. Supports automatic fallback from primary to secondary provider and
exponential backoff retry on transient failures.

Usage:
    from src.agent.llm_provider import LLMProvider

    provider = LLMProvider()
    response = await provider.generate("Explain this user story")
    parsed = await provider.generate_structured(prompt, TestScenario)
"""

import json
from typing import TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.common.exceptions import (
    LLMProviderError,
    LLMResponseParseError,
    LLMTimeoutError,
)
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMProvider:
    """Unified LLM provider with fallback and structured output support.

    Manages the lifecycle of LLM connections, provides retry logic
    with exponential backoff, and supports parsing LLM responses into
    Pydantic models for type-safe downstream processing.
    """

    def __init__(self) -> None:
        """Initialize with settings-based provider configuration."""
        self._settings = get_settings()
        self._primary_provider = self._settings.llm_provider
        self._fallback_provider = (
            "gemini" if self._primary_provider == "ollama" else "ollama"
        )
        self._max_retries = self._settings.ollama.max_retries

        self._primary_llm: BaseChatModel | None = None
        self._fallback_llm: BaseChatModel | None = None

    @property
    def primary_llm(self) -> BaseChatModel:
        """Lazy-initialize and return the primary LLM instance."""
        if self._primary_llm is None:
            self._primary_llm = self._create_llm(self._primary_provider)
        return self._primary_llm

    @property
    def fallback_llm(self) -> BaseChatModel:
        """Lazy-initialize and return the fallback LLM instance."""
        if self._fallback_llm is None:
            self._fallback_llm = self._create_llm(self._fallback_provider)
        return self._fallback_llm

    def _create_llm(self, provider: str) -> BaseChatModel:
        """Create an LLM instance for the given provider.

        Args:
            provider: Either "ollama" or "gemini".

        Returns:
            A LangChain BaseChatModel instance.

        Raises:
            LLMProviderError: If the provider cannot be instantiated.
        """
        if provider == "ollama":
            return self._create_ollama()
        elif provider == "gemini":
            return self._create_gemini()
        else:
            raise LLMProviderError(
                provider=provider,
                reason=f"Unknown provider: {provider}",
            )

    def _create_ollama(self) -> BaseChatModel:
        """Create an Ollama chat model instance."""
        try:
            from langchain_community.chat_models import ChatOllama

            return ChatOllama(
                model=self._settings.ollama.model,
                base_url=self._settings.ollama.base_url,
                timeout=self._settings.ollama.timeout,
                temperature=0.1,
            )
        except ImportError as e:
            raise LLMProviderError(
                provider="ollama",
                reason="langchain-community not installed",
            ) from e
        except Exception as e:
            raise LLMProviderError(provider="ollama", reason=str(e)) from e

    def _create_gemini(self) -> BaseChatModel:
        """Create a Google Gemini chat model instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            if not self._settings.gemini.api_key:
                raise LLMProviderError(
                    provider="gemini",
                    reason="GEMINI_API_KEY not configured",
                )

            return ChatGoogleGenerativeAI(
                model=self._settings.gemini.model,
                google_api_key=self._settings.gemini.api_key,
                temperature=0.1,
                max_retries=self._settings.gemini.max_retries,
            )
        except ImportError as e:
            raise LLMProviderError(
                provider="gemini",
                reason="langchain-google-genai not installed",
            ) from e
        except LLMProviderError:
            raise
        except Exception as e:
            raise LLMProviderError(provider="gemini", reason=str(e)) from e

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Generate a text response from the LLM with fallback.

        Tries the primary provider first; on failure, falls back to
        the secondary provider.

        Args:
            prompt: The user/task prompt.
            system_prompt: Optional system-level instructions.

        Returns:
            The LLM's text response.

        Raises:
            LLMProviderError: If both providers fail after retries.
        """
        messages = self._build_messages(prompt, system_prompt)

        # Try primary
        try:
            response = await self._invoke_with_retry(self.primary_llm, messages)
            return response
        except (LLMProviderError, LLMTimeoutError) as primary_err:
            logger.warning(
                "primary_llm_failed_trying_fallback",
                provider=self._primary_provider,
                error=str(primary_err),
            )

        # Try fallback
        try:
            response = await self._invoke_with_retry(self.fallback_llm, messages)
            return response
        except (LLMProviderError, LLMTimeoutError) as fallback_err:
            raise LLMProviderError(
                provider=f"{self._primary_provider}+{self._fallback_provider}",
                reason=(
                    f"Both providers failed. "
                    f"Primary: {primary_err.message}. "  # noqa: F821
                    f"Fallback: {fallback_err.message}"
                ),
            ) from fallback_err

    async def generate_structured(
        self,
        prompt: str,
        output_model: type[T],
        system_prompt: str | None = None,
    ) -> T:
        """Generate a structured response parsed into a Pydantic model.

        Instructs the LLM to return JSON matching the Pydantic schema,
        then validates and parses the response.

        Args:
            prompt: The user/task prompt.
            output_model: The Pydantic model class to parse into.
            system_prompt: Optional system-level instructions.

        Returns:
            An instance of output_model populated with LLM response data.

        Raises:
            LLMResponseParseError: If the response cannot be parsed.
            LLMProviderError: If both providers fail.
        """
        # Build schema-aware prompt
        schema_json = json.dumps(output_model.model_json_schema(), indent=2)
        structured_prompt = (
            f"{prompt}\n\n"
            f"Respond ONLY with valid JSON matching this schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Do not include any text outside the JSON object."
        )

        raw_response = await self.generate(structured_prompt, system_prompt)

        # Parse the response
        return self._parse_response(raw_response, output_model)

    def _parse_response(self, raw_response: str, output_model: type[T]) -> T:
        """Parse raw LLM response text into a Pydantic model.

        Handles common LLM response quirks (markdown code blocks, extra text).

        Args:
            raw_response: The raw text from the LLM.
            output_model: The Pydantic model to parse into.

        Returns:
            Parsed model instance.

        Raises:
            LLMResponseParseError: If parsing fails.
        """
        # Strip markdown code fences if present
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return output_model.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            raise LLMResponseParseError(
                expected_schema=output_model.__name__,
                raw_response=raw_response,
            ) from e

    def _build_messages(
        self, prompt: str, system_prompt: str | None
    ) -> list[SystemMessage | HumanMessage]:
        """Build the message list for the LLM call."""
        messages: list[SystemMessage | HumanMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        return messages

    async def _invoke_with_retry(
        self,
        llm: BaseChatModel,
        messages: list[SystemMessage | HumanMessage],
    ) -> str:
        """Invoke the LLM with exponential backoff retry.

        Retries up to max_retries times on transient failures.

        Args:
            llm: The LangChain chat model to call.
            messages: Messages to send.

        Returns:
            The text content of the LLM response.

        Raises:
            LLMProviderError: On non-transient or exhausted retries.
            LLMTimeoutError: On timeout after all retries.
        """

        @retry(
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            retry=retry_if_exception_type((TimeoutError, ConnectionError, OSError)),
            reraise=True,
        )
        async def _call() -> str:
            try:
                response = await llm.ainvoke(messages)
                return str(response.content)
            except TimeoutError as e:
                logger.warning("llm_timeout", attempt="retrying")
                raise LLMTimeoutError(
                    provider=self._primary_provider,
                    timeout_seconds=self._settings.ollama.timeout,
                ) from e
            except (ConnectionError, OSError):
                logger.warning("llm_connection_error", attempt="retrying")
                raise

        try:
            return await _call()
        except LLMTimeoutError:
            raise
        except Exception as e:
            raise LLMProviderError(
                provider="unknown",
                reason=f"Exhausted retries: {e}",
            ) from e
