"""Unit tests for RAG retriever service."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.rag.retriever import RetrievalResult, StoryRetriever


@pytest.fixture
def mock_vectorstore():
    """Create a mock VectorStoreManager."""
    mock = MagicMock()
    mock.similarity_search_with_score.return_value = [
        (Document(page_content="Login story content", metadata={"story_id": "US-001"}), 0.3),
        (Document(page_content="Dashboard story", metadata={"story_id": "US-002"}), 0.5),
        (Document(page_content="Unrelated content", metadata={"story_id": "US-099"}), 0.9),
    ]
    return mock


class TestRetrievalResult:
    """Tests for the RetrievalResult dataclass."""

    @pytest.mark.unit
    def test_count_returns_document_count(self):
        result = RetrievalResult(
            documents=[Document(page_content="a"), Document(page_content="b")],
            scores=[0.2, 0.4],
            query="test",
        )
        assert result.count == 2

    @pytest.mark.unit
    def test_is_empty_when_no_documents(self):
        result = RetrievalResult(documents=[], scores=[], query="test")
        assert result.is_empty is True

    @pytest.mark.unit
    def test_is_not_empty_when_has_documents(self):
        result = RetrievalResult(
            documents=[Document(page_content="doc")],
            scores=[0.1],
            query="test",
        )
        assert result.is_empty is False

    @pytest.mark.unit
    def test_to_context_string_combines_documents(self):
        result = RetrievalResult(
            documents=[
                Document(page_content="First doc"),
                Document(page_content="Second doc"),
            ],
            scores=[0.2, 0.4],
            query="test",
        )
        context = result.to_context_string()
        assert "First doc" in context
        assert "Second doc" in context
        assert "---" in context  # default separator


class TestStoryRetriever:
    """Tests for StoryRetriever with mocked vector store."""

    @pytest.mark.unit
    @patch("src.rag.retriever.get_settings")
    @patch("src.rag.retriever.VectorStoreManager")
    def test_retrieve_applies_threshold_filtering(
        self, mock_vs_class, mock_settings, mock_vectorstore
    ):
        """Verify documents above threshold are filtered out."""
        mock_settings.return_value.rag.top_k = 3
        mock_settings.return_value.rag.similarity_threshold = 0.7

        retriever = StoryRetriever(
            vectorstore_manager=mock_vectorstore,
            top_k=3,
            similarity_threshold=0.7,
        )
        result = retriever.retrieve("login tests")

        # Score 0.9 should be filtered out (above 0.7 threshold)
        assert result.count == 2
        assert result.total_candidates == 3
        assert all(s <= 0.7 for s in result.scores)

    @pytest.mark.unit
    @patch("src.rag.retriever.get_settings")
    @patch("src.rag.retriever.VectorStoreManager")
    def test_retrieve_with_metadata_filter(
        self, mock_vs_class, mock_settings, mock_vectorstore
    ):
        """Verify metadata filter is passed to vector store."""
        mock_settings.return_value.rag.top_k = 3
        mock_settings.return_value.rag.similarity_threshold = 1.0

        retriever = StoryRetriever(
            vectorstore_manager=mock_vectorstore,
            top_k=3,
            similarity_threshold=1.0,
        )
        retriever.retrieve("test", filter_epic="Auth")

        # Check that filter was passed
        call_kwargs = mock_vectorstore.similarity_search_with_score.call_args[1]
        assert call_kwargs["filter_metadata"] == {"epic": {"$eq": "Auth"}}

    @pytest.mark.unit
    @patch("src.rag.retriever.get_settings")
    @patch("src.rag.retriever.VectorStoreManager")
    def test_retrieve_context_returns_string(
        self, mock_vs_class, mock_settings, mock_vectorstore
    ):
        """Verify retrieve_context returns combined text."""
        mock_settings.return_value.rag.top_k = 3
        mock_settings.return_value.rag.similarity_threshold = 1.0

        retriever = StoryRetriever(
            vectorstore_manager=mock_vectorstore,
            top_k=3,
            similarity_threshold=1.0,
        )
        context = retriever.retrieve_context("login")

        assert isinstance(context, str)
        assert "Login story content" in context

    @pytest.mark.unit
    @patch("src.rag.retriever.get_settings")
    @patch("src.rag.retriever.VectorStoreManager")
    def test_retrieve_empty_results(self, mock_vs_class, mock_settings):
        """Verify empty results when vector store returns nothing."""
        mock_settings.return_value.rag.top_k = 3
        mock_settings.return_value.rag.similarity_threshold = 0.7

        mock_vs = MagicMock()
        mock_vs.similarity_search_with_score.return_value = []

        retriever = StoryRetriever(
            vectorstore_manager=mock_vs,
            top_k=3,
            similarity_threshold=0.7,
        )
        result = retriever.retrieve("nothing matches")

        assert result.is_empty
        assert result.count == 0
