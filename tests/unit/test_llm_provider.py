"""Unit tests for LLM provider abstraction."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent.llm_provider import LLMProvider
from src.agent.state import TestScenario
from src.common.exceptions import LLMProviderError, LLMResponseParseError


class TestLLMProviderParsing:
    """Tests for LLM response parsing logic."""

    @pytest.mark.unit
    def test_parse_clean_json(self):
        """Verify clean JSON is parsed into a Pydantic model."""
        provider = LLMProvider.__new__(LLMProvider)
        provider._settings = MagicMock()
        provider._primary_provider = "ollama"

        raw = json.dumps({
            "title": "Login test",
            "description": "Test login functionality",
            "priority": "P1",
            "test_type": "smoke",
            "preconditions": [],
            "steps": [],
            "tags": ["login"],
            "story_id": "US-001",
        })

        result = provider._parse_response(raw, TestScenario)
        assert isinstance(result, TestScenario)
        assert result.title == "Login test"
        assert result.priority == "P1"

    @pytest.mark.unit
    def test_parse_json_with_markdown_fences(self):
        """Verify JSON wrapped in markdown code blocks is handled."""
        provider = LLMProvider.__new__(LLMProvider)
        provider._settings = MagicMock()
        provider._primary_provider = "ollama"

        raw = """```json
{
    "title": "Dashboard test",
    "description": "Test dashboard",
    "priority": "P2",
    "test_type": "regression"
}
```"""

        result = provider._parse_response(raw, TestScenario)
        assert result.title == "Dashboard test"

    @pytest.mark.unit
    def test_parse_invalid_json_raises_error(self):
        """Verify invalid JSON raises LLMResponseParseError."""
        provider = LLMProvider.__new__(LLMProvider)
        provider._settings = MagicMock()
        provider._primary_provider = "ollama"

        raw = "This is not JSON at all"

        with pytest.raises(LLMResponseParseError) as exc_info:
            provider._parse_response(raw, TestScenario)
        assert "TestScenario" in exc_info.value.message

    @pytest.mark.unit
    def test_parse_json_missing_required_fields(self):
        """Verify missing required fields raises parse error."""
        provider = LLMProvider.__new__(LLMProvider)
        provider._settings = MagicMock()
        provider._primary_provider = "ollama"

        raw = json.dumps({"not_a_valid_field": "value"})

        with pytest.raises(LLMResponseParseError):
            provider._parse_response(raw, TestScenario)


class TestLLMProviderInit:
    """Tests for LLM provider initialization."""

    @pytest.mark.unit
    @patch("src.agent.llm_provider.get_settings")
    def test_default_provider_from_settings(self, mock_settings):
        """Verify primary provider comes from settings."""
        mock_settings.return_value.llm_provider = "gemini"
        mock_settings.return_value.ollama.max_retries = 3
        mock_settings.return_value.ollama.model = "llama3.2"
        mock_settings.return_value.ollama.base_url = "http://localhost:11434"
        mock_settings.return_value.ollama.timeout = 120
        mock_settings.return_value.gemini.api_key = "test-key"
        mock_settings.return_value.gemini.model = "gemini-2.5-flash"
        mock_settings.return_value.gemini.max_retries = 3

        provider = LLMProvider()
        assert provider._primary_provider == "gemini"
        assert provider._fallback_provider == "ollama"

    @pytest.mark.unit
    @patch("src.agent.llm_provider.get_settings")
    def test_ollama_primary_gemini_fallback(self, mock_settings):
        """Verify ollama primary means gemini fallback."""
        mock_settings.return_value.llm_provider = "ollama"
        mock_settings.return_value.ollama.max_retries = 3

        provider = LLMProvider()
        assert provider._primary_provider == "ollama"
        assert provider._fallback_provider == "gemini"


class TestLLMProviderGenerate:
    """Tests for the generate method with mocked LLM."""

    @pytest.mark.unit
    @patch("src.agent.llm_provider.get_settings")
    async def test_generate_returns_text(self, mock_settings):
        """Verify generate returns string response from mocked LLM."""
        mock_settings.return_value.llm_provider = "ollama"
        mock_settings.return_value.ollama.max_retries = 3
        mock_settings.return_value.ollama.timeout = 120

        provider = LLMProvider()

        # Mock the primary LLM
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(content="Generated text response")
        provider._primary_llm = mock_llm

        result = await provider.generate("Test prompt")
        assert result == "Generated text response"

    @pytest.mark.unit
    @patch("src.agent.llm_provider.get_settings")
    async def test_generate_falls_back_on_failure(self, mock_settings):
        """Verify fallback is used when primary raises an error."""
        mock_settings.return_value.llm_provider = "ollama"
        mock_settings.return_value.ollama.max_retries = 1
        mock_settings.return_value.ollama.timeout = 5

        provider = LLMProvider()

        # Primary fails
        mock_primary = AsyncMock()
        mock_primary.ainvoke.side_effect = ConnectionError("Ollama down")
        provider._primary_llm = mock_primary

        # Fallback succeeds
        mock_fallback = AsyncMock()
        mock_fallback.ainvoke.return_value = MagicMock(content="Fallback response")
        provider._fallback_llm = mock_fallback

        result = await provider.generate("Test prompt")
        assert result == "Fallback response"
