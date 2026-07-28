"""Integration tests for the full agent pipeline: story → task.

Tests the LangGraph agent flow end-to-end with mocked LLM provider
and vector store to verify state transitions and data flow.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.agent.state import AgentState, TestGenerationResult, TestScenario, TestStep


class TestAgentIngestNode:
    """Tests for the ingest node integration."""

    @pytest.mark.integration
    @patch("src.agent.nodes.ingest.get_settings")
    @patch("src.agent.nodes.ingest.StoryRetriever")
    async def test_ingest_retrieves_context(self, mock_retriever_class, mock_settings):
        """Verify ingest node populates retrieved_docs from vector store."""
        from src.agent.nodes.ingest import ingest_node
        from src.rag.retriever import RetrievalResult

        mock_settings.return_value.rag.top_k = 3
        mock_settings.return_value.rag.similarity_threshold = 0.7

        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = RetrievalResult(
            documents=[
                Document(page_content="Related login story", metadata={"story_id": "US-001"}),
            ],
            scores=[0.3],
            query="login",
            total_candidates=5,
        )
        mock_retriever_class.return_value = mock_retriever

        state: AgentState = {
            "user_story_text": "As a user I want to log in",
            "target_url": None,
            "retrieved_docs": [],
            "test_scenarios": [],
            "site_map": None,
            "crawl_results": None,
            "plane_task_id": None,
            "plane_task_ids": [],
            "execution_status": "pending",
            "current_node": "start",
            "error_message": None,
            "retry_count": 0,
        }

        result = await ingest_node(state)
        assert result["current_node"] == "ingest"
        assert len(result["retrieved_docs"]) == 1
        assert result["retrieved_docs"][0].page_content == "Related login story"

    @pytest.mark.integration
    @patch("src.agent.nodes.ingest.get_settings")
    @patch("src.agent.nodes.ingest.StoryRetriever")
    async def test_ingest_degrades_gracefully_on_failure(
        self, mock_retriever_class, mock_settings
    ):
        """Verify ingest continues with empty docs if RAG fails."""
        mock_settings.return_value.rag.top_k = 3
        mock_settings.return_value.rag.similarity_threshold = 0.7

        mock_retriever = MagicMock()
        mock_retriever.retrieve.side_effect = Exception("ChromaDB unavailable")
        mock_retriever_class.return_value = mock_retriever

        state: AgentState = {
            "user_story_text": "As a user I want to log in",
            "target_url": None,
            "retrieved_docs": [],
            "test_scenarios": [],
            "site_map": None,
            "crawl_results": None,
            "plane_task_id": None,
            "plane_task_ids": [],
            "execution_status": "pending",
            "current_node": "start",
            "error_message": None,
            "retry_count": 0,
        }

        result = await ingest_node(state)
        assert result["retrieved_docs"] == []
        assert "RAG retrieval failed" in result.get("error_message", "")


class TestAgentGenerateNode:
    """Tests for the generate node integration."""

    @pytest.mark.integration
    @patch("src.agent.nodes.generate.LLMProvider")
    async def test_generate_produces_scenarios(self, mock_provider_class):
        """Verify generate node returns test scenarios from LLM."""
        from src.agent.nodes.generate import generate_node

        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = TestGenerationResult(
            scenarios=[
                TestScenario(
                    title="Login success test",
                    description="Verify login with valid credentials",
                    priority="P1",
                    test_type="smoke",
                    steps=[TestStep(action="Enter email", expected_result="Email shown")],
                    tags=["login", "auth"],
                    story_id="US-001",
                ),
                TestScenario(
                    title="Login error test",
                    description="Verify invalid password shows error",
                    priority="P1",
                    test_type="regression",
                    tags=["login", "validation"],
                    story_id="US-001",
                ),
            ],
            source_story_summary="Login user story",
            coverage_notes="Covers happy path and error",
        )
        mock_provider_class.return_value = mock_provider

        state: AgentState = {
            "user_story_text": "As a user I want to log in with email and password",
            "target_url": None,
            "retrieved_docs": [
                Document(page_content="Related context", metadata={"story_id": "US-001"})
            ],
            "test_scenarios": [],
            "site_map": None,
            "crawl_results": None,
            "plane_task_id": None,
            "plane_task_ids": [],
            "execution_status": "pending",
            "current_node": "ingest",
            "error_message": None,
            "retry_count": 0,
        }

        result = await generate_node(state)
        assert result["current_node"] == "generate"
        assert len(result["test_scenarios"]) == 2
        assert result["test_scenarios"][0].title == "Login success test"
        assert result["test_scenarios"][0].priority == "P1"

    @pytest.mark.integration
    @patch("src.agent.nodes.generate.LLMProvider")
    async def test_generate_handles_llm_failure(self, mock_provider_class):
        """Verify generate node returns empty scenarios on LLM error."""
        from src.agent.nodes.generate import generate_node
        from src.common.exceptions import LLMProviderError

        mock_provider = AsyncMock()
        mock_provider.generate_structured.side_effect = LLMProviderError(
            provider="ollama+gemini", reason="Both providers failed"
        )
        mock_provider_class.return_value = mock_provider

        state: AgentState = {
            "user_story_text": "Some story",
            "target_url": None,
            "retrieved_docs": [],
            "test_scenarios": [],
            "site_map": None,
            "crawl_results": None,
            "plane_task_id": None,
            "plane_task_ids": [],
            "execution_status": "pending",
            "current_node": "ingest",
            "error_message": None,
            "retry_count": 0,
        }

        result = await generate_node(state)
        assert result["test_scenarios"] == []
        assert "Test generation failed" in result.get("error_message", "")


class TestAgentGraphRouting:
    """Tests for conditional edge routing logic."""

    @pytest.mark.integration
    def test_route_after_generate_to_prioritize_with_scenarios(self):
        """Verify routing goes to prioritize when scenarios exist."""
        from src.agent.graph import route_after_generate

        state: AgentState = {
            "user_story_text": "",
            "target_url": None,
            "retrieved_docs": [],
            "test_scenarios": [
                TestScenario(title="Test", description="Desc")
            ],
            "site_map": None,
            "crawl_results": None,
            "plane_task_id": None,
            "plane_task_ids": [],
            "execution_status": "pending",
            "current_node": "generate",
            "error_message": None,
            "retry_count": 0,
        }

        assert route_after_generate(state) == "prioritize"

    @pytest.mark.integration
    def test_route_after_generate_retries_when_empty(self):
        """Verify routing retries generate when scenarios empty and retries left."""
        from src.agent.graph import route_after_generate

        state: AgentState = {
            "user_story_text": "",
            "target_url": None,
            "retrieved_docs": [],
            "test_scenarios": [],
            "site_map": None,
            "crawl_results": None,
            "plane_task_id": None,
            "plane_task_ids": [],
            "execution_status": "pending",
            "current_node": "generate",
            "error_message": "LLM failed",
            "retry_count": 0,
        }

        assert route_after_generate(state) == "generate"

    @pytest.mark.integration
    def test_route_after_generate_ends_when_retries_exhausted(self):
        """Verify routing ends when retries are exhausted."""
        from langgraph.graph import END

        from src.agent.graph import route_after_generate

        state: AgentState = {
            "user_story_text": "",
            "target_url": None,
            "retrieved_docs": [],
            "test_scenarios": [],
            "site_map": None,
            "crawl_results": None,
            "plane_task_id": None,
            "plane_task_ids": [],
            "execution_status": "pending",
            "current_node": "generate",
            "error_message": "Failed",
            "retry_count": 3,
        }

        assert route_after_generate(state) == END
