"""Story retriever service for semantic search of user stories.

Provides the main interface for retrieving relevant user story context
given a query. Applies similarity threshold filtering and metadata-based
narrowing to ensure high-quality context for test generation.

Usage:
    from src.rag.retriever import StoryRetriever

    retriever = StoryRetriever()
    results = retriever.retrieve("login functionality tests")
"""

from dataclasses import dataclass, field

from langchain_core.documents import Document

from src.common.logging import get_logger
from src.config.settings import get_settings
from src.rag.vectorstore import VectorStoreManager

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """Container for retrieval results with scores and metadata.

    Attributes:
        documents: List of retrieved Document objects.
        scores: Corresponding similarity scores (lower = more similar for cosine).
        query: The original query text.
        total_candidates: Number of candidates before threshold filtering.
    """

    documents: list[Document] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)
    query: str = ""
    total_candidates: int = 0

    @property
    def count(self) -> int:
        """Number of retrieved documents."""
        return len(self.documents)

    @property
    def is_empty(self) -> bool:
        """Whether the retrieval returned no results."""
        return len(self.documents) == 0

    def to_context_string(self, separator: str = "\n\n---\n\n") -> str:
        """Combine all retrieved documents into a single context string.

        Args:
            separator: String to place between documents.

        Returns:
            Combined text of all retrieved documents.
        """
        return separator.join(doc.page_content for doc in self.documents)


class StoryRetriever:
    """Service for retrieving relevant user stories from the vector store.

    Wraps VectorStoreManager with threshold filtering, metadata narrowing,
    and result formatting suitable for LLM context injection.
    """

    def __init__(
        self,
        vectorstore_manager: VectorStoreManager | None = None,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
    ) -> None:
        """Initialize the story retriever.

        Args:
            vectorstore_manager: Existing VectorStoreManager instance.
                Creates a new one if not provided.
            top_k: Maximum number of results to return. Defaults to settings.
            similarity_threshold: Maximum distance score to accept.
                Documents with scores above this are filtered out.
                Defaults to settings value.
        """
        settings = get_settings()
        self._top_k = top_k if top_k is not None else settings.rag.top_k
        self._threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.rag.similarity_threshold
        )
        self._vectorstore = vectorstore_manager or VectorStoreManager()

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter_epic: str | None = None,
        filter_feature: str | None = None,
        filter_role: str | None = None,
    ) -> RetrievalResult:
        """Retrieve relevant user stories for a given query.

        Performs similarity search with optional metadata filtering and
        threshold-based quality gating.

        Args:
            query: The search query (e.g., "login page validation tests").
            top_k: Override the default number of results.
            filter_epic: Only return stories from this epic.
            filter_feature: Only return stories for this feature.
            filter_role: Only return stories for this target role.

        Returns:
            RetrievalResult with filtered documents and scores.
        """
        k = top_k or self._top_k

        # Build metadata filter
        metadata_filter = self._build_filter(filter_epic, filter_feature, filter_role)

        # Perform search with scores for threshold filtering
        raw_results = self._vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter_metadata=metadata_filter,
        )

        # Apply similarity threshold
        filtered_docs: list[Document] = []
        filtered_scores: list[float] = []

        for doc, score in raw_results:
            if score <= self._threshold:
                filtered_docs.append(doc)
                filtered_scores.append(score)

        result = RetrievalResult(
            documents=filtered_docs,
            scores=filtered_scores,
            query=query,
            total_candidates=len(raw_results),
        )

        logger.info(
            "retrieval_completed",
            query=query[:80],
            total_candidates=result.total_candidates,
            after_threshold=result.count,
            threshold=self._threshold,
        )

        return result

    def retrieve_context(
        self,
        query: str,
        top_k: int | None = None,
        filter_epic: str | None = None,
        filter_feature: str | None = None,
    ) -> str:
        """Retrieve and format context as a single string for LLM prompts.

        Convenience method that returns the combined text of all matching
        documents, ready to be injected into a prompt template.

        Args:
            query: The search query.
            top_k: Override the default number of results.
            filter_epic: Only return stories from this epic.
            filter_feature: Only return stories for this feature.

        Returns:
            Combined text string of relevant user stories, or empty string
            if no matches found.
        """
        result = self.retrieve(
            query=query,
            top_k=top_k,
            filter_epic=filter_epic,
            filter_feature=filter_feature,
        )

        if result.is_empty:
            logger.warning("no_context_found", query=query[:80])
            return ""

        return result.to_context_string()

    def _build_filter(
        self,
        epic: str | None,
        feature: str | None,
        role: str | None,
    ) -> dict | None:
        """Build a ChromaDB metadata filter from optional parameters.

        Args:
            epic: Epic name filter.
            feature: Feature name filter.
            role: Target role filter.

        Returns:
            ChromaDB where clause dict, or None if no filters specified.
        """
        conditions: list[dict] = []

        if epic:
            conditions.append({"epic": {"$eq": epic}})
        if feature:
            conditions.append({"feature": {"$eq": feature}})
        if role:
            conditions.append({"target_role": {"$eq": role}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}
