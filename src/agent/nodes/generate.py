"""Generate node for the LangGraph agent.

Produces test scenarios from user stories (or site analysis results)
using the LLM provider. Handles both story-based and URL-based flows.
"""

from src.agent.llm_provider import LLMProvider
from src.agent.prompts.site_analysis import build_site_analysis_prompt, format_pages_for_prompt
from src.agent.prompts.test_generation import build_test_generation_prompt
from src.agent.state import AgentState, TestGenerationResult, TestScenario
from src.common.exceptions import LLMProviderError, LLMResponseParseError
from src.common.logging import get_logger

logger = get_logger(__name__)


async def generate_node(state: AgentState) -> dict:
    """Generate test scenarios from the user story or crawl results.

    Routes to either story-based or site-analysis-based generation
    depending on available state data.

    Args:
        state: Current agent state with user_story_text and/or crawl_results.

    Returns:
        State update dict with test_scenarios and current_node.
    """
    logger.info(
        "generate_node_started",
        has_story=bool(state.get("user_story_text", "").strip()),
        has_crawl_results=state.get("crawl_results") is not None,
    )

    # Determine which generation path to take
    if state.get("crawl_results") is not None:
        return await _generate_from_crawl(state)
    else:
        return await _generate_from_story(state)


async def _generate_from_story(state: AgentState) -> dict:
    """Generate test scenarios from a user story with RAG context.

    Args:
        state: Agent state with user_story_text and retrieved_docs.

    Returns:
        State update with generated test_scenarios.
    """
    user_story = state["user_story_text"]

    # Build RAG context from retrieved documents
    rag_context = ""
    retrieved_docs = state.get("retrieved_docs", [])
    if retrieved_docs:
        context_parts = [doc.page_content for doc in retrieved_docs]
        rag_context = "\n\n---\n\n".join(context_parts)

    # Determine story_id from metadata if available
    story_id = ""
    if retrieved_docs:
        first_doc_meta = retrieved_docs[0].metadata
        story_id = first_doc_meta.get("story_id", "")

    # Build prompt
    system_prompt, user_prompt = build_test_generation_prompt(
        user_story=user_story,
        rag_context=rag_context,
        story_id=story_id,
    )

    # Generate with structured output
    provider = LLMProvider()

    try:
        result = await provider.generate_structured(
            prompt=user_prompt,
            output_model=TestGenerationResult,
            system_prompt=system_prompt,
        )

        scenarios = result.scenarios
        logger.info(
            "test_generation_completed",
            scenarios_count=len(scenarios),
            coverage_notes=result.coverage_notes[:100],
        )

        return {
            "test_scenarios": scenarios,
            "current_node": "generate",
        }

    except (LLMProviderError, LLMResponseParseError) as e:
        logger.error("test_generation_failed", error=str(e))
        return {
            "test_scenarios": [],
            "current_node": "generate",
            "error_message": f"Test generation failed: {e.message}",
        }


async def _generate_from_crawl(state: AgentState) -> dict:
    """Generate test scenarios from site crawl results.

    Args:
        state: Agent state with crawl_results populated.

    Returns:
        State update with generated test_scenarios.
    """
    crawl_results = state["crawl_results"]
    if crawl_results is None:
        return {
            "test_scenarios": [],
            "current_node": "generate",
            "error_message": "No crawl results available for generation",
        }

    site_map = crawl_results.site_map

    # Format pages for the prompt
    pages_data = [
        {
            "url": page.url,
            "title": page.title,
            "depth": page.depth,
            "elements": [elem.model_dump() for elem in page.elements],
            "links": page.links,
        }
        for page in site_map.pages
    ]
    pages_detail = format_pages_for_prompt(pages_data)

    # Build prompt
    system_prompt, user_prompt = build_site_analysis_prompt(
        start_url=site_map.start_url,
        total_pages=site_map.total_pages,
        max_depth=site_map.max_depth_reached,
        pages_detail=pages_detail,
        suggested_flows=crawl_results.suggested_flows,
    )

    # Generate with structured output
    provider = LLMProvider()

    try:
        result = await provider.generate_structured(
            prompt=user_prompt,
            output_model=TestGenerationResult,
            system_prompt=system_prompt,
        )

        scenarios = result.scenarios
        logger.info(
            "site_analysis_generation_completed",
            scenarios_count=len(scenarios),
            source_url=site_map.start_url,
        )

        return {
            "test_scenarios": scenarios,
            "current_node": "generate",
        }

    except (LLMProviderError, LLMResponseParseError) as e:
        logger.error("site_analysis_generation_failed", error=str(e))
        return {
            "test_scenarios": [],
            "current_node": "generate",
            "error_message": f"Site analysis generation failed: {e.message}",
        }
