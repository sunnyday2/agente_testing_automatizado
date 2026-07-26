"""Ingest node for the LangGraph agent.

Handles user story ingestion: loads the story text, retrieves relevant
context from the RAG vector store, and populates the agent state with
retrieved documents for downstream processing.
"""

from src.agent.state import AgentState
from src.common.logging import get_logger
from src.config.settings import get_settings
from src.rag.retriever import StoryRetriever

logger = get_logger(__name__)


async def ingest_node(state: AgentState) -> dict:
    """Ingest a user story and retrieve related context from the vector store.

    This is the entry node of the agent graph. It takes the raw user story
    text and performs similarity search to find related stories that provide
    additional context for test generation.

    Args:
        state: Current agent state with user_story_text populated.

    Returns:
        State update dict with retrieved_docs and current_node.
    """
    user_story = state["user_story_text"]

    logger.info(
        "ingest_node_started",
        story_length=len(user_story),
        has_target_url=bool(state.get("target_url")),
    )

    # Skip RAG if this is a URL-based flow (no story to match against)
    if not user_story.strip():
        logger.info("ingest_skipped_no_story_text")
        return {
            "retrieved_docs": [],
            "current_node": "ingest",
        }

    # Retrieve related context from vector store
    try:
        settings = get_settings()
        retriever = StoryRetriever(
            top_k=settings.rag.top_k,
            similarity_threshold=settings.rag.similarity_threshold,
        )
        result = retriever.retrieve(query=user_story)

        logger.info(
            "ingest_retrieval_completed",
            retrieved_count=result.count,
            total_candidates=result.total_candidates,
        )

        return {
            "retrieved_docs": result.documents,
            "current_node": "ingest",
        }

    except Exception as e:
        # Graceful degradation: continue without RAG context on failure
        logger.warning(
            "ingest_retrieval_failed_continuing_without_context",
            error=str(e),
        )
        return {
            "retrieved_docs": [],
            "current_node": "ingest",
            "error_message": f"RAG retrieval failed: {e}",
        }
