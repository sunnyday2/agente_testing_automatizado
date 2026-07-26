"""LangGraph state machine definition for the QA Automation Agent.

Defines the full agent graph with nodes, edges, conditional routing,
retry logic, and checkpointing support for recovery.

Graph Flow:
    START → ingest → generate → route_after_generate
        ├── (has scenarios) → prioritize → publish → END
        └── (empty/error + retries left) → generate (retry)
        └── (empty/error + retries exhausted) → END

Usage:
    from src.agent.graph import create_agent_graph, run_agent

    # Create the compiled graph
    graph = create_agent_graph()

    # Run with a user story
    result = await run_agent(user_story_text="As a user I want...")

    # Run with a target URL (crawl-based flow)
    result = await run_agent(target_url="https://example.com")
"""

from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agent.nodes.generate import generate_node
from src.agent.nodes.ingest import ingest_node
from src.agent.nodes.prioritize import prioritize_node
from src.agent.nodes.publish import publish_node
from src.agent.state import AgentState
from src.common.logging import get_logger

logger = get_logger(__name__)

# Maximum retry attempts for the generate node
MAX_GENERATE_RETRIES = 2


def route_after_generate(state: AgentState) -> Literal["prioritize", "generate", "__end__"]:
    """Conditional routing after the generate node.

    Determines the next step based on generation results:
    - If scenarios were generated → proceed to prioritize
    - If empty but retries remain → retry generate
    - If empty and retries exhausted → end with error

    Args:
        state: Current agent state after generate node.

    Returns:
        The name of the next node to execute.
    """
    scenarios = state.get("test_scenarios", [])
    retry_count = state.get("retry_count", 0)

    if scenarios:
        logger.info(
            "route_after_generate_to_prioritize",
            scenarios_count=len(scenarios),
        )
        return "prioritize"

    if retry_count < MAX_GENERATE_RETRIES:
        logger.warning(
            "route_after_generate_retry",
            retry_count=retry_count,
            max_retries=MAX_GENERATE_RETRIES,
        )
        return "generate"

    logger.error(
        "route_after_generate_exhausted",
        retry_count=retry_count,
        error=state.get("error_message", "Unknown error"),
    )
    return END


def route_after_prioritize(state: AgentState) -> Literal["publish", "__end__"]:
    """Conditional routing after the prioritize node.

    Determines whether to proceed to publish or end:
    - If scenarios exist → publish to Plane.so
    - If no scenarios (unlikely after prioritize) → end

    Args:
        state: Current agent state after prioritize node.

    Returns:
        The name of the next node to execute.
    """
    scenarios = state.get("test_scenarios", [])
    if scenarios:
        return "publish"
    return END


async def increment_retry(state: AgentState) -> dict:
    """Pre-generate hook that increments the retry counter.

    This wrapper is used when the generate node is being retried,
    so we can track how many attempts have been made.

    Args:
        state: Current agent state.

    Returns:
        State update with incremented retry_count.
    """
    current = state.get("retry_count", 0)
    return {"retry_count": current + 1}


def create_agent_graph(checkpointer=None) -> StateGraph:
    """Create and compile the full agent state graph.

    Builds the LangGraph state machine with all nodes, edges,
    conditional routing, and optional checkpointing.

    Args:
        checkpointer: Optional LangGraph checkpointer for state persistence.
            If None, uses MemorySaver for in-memory checkpointing.

    Returns:
        A compiled StateGraph ready for execution.
    """
    # Use MemorySaver by default for recovery support
    if checkpointer is None:
        checkpointer = MemorySaver()

    # Define the graph
    workflow = StateGraph(AgentState)

    # --- Add Nodes ---
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("prioritize", prioritize_node)
    workflow.add_node("publish", publish_node)

    # --- Add Edges ---

    # START → ingest (always the entry point)
    workflow.add_edge(START, "ingest")

    # ingest → generate (always proceeds to generation)
    workflow.add_edge("ingest", "generate")

    # generate → conditional routing (check results)
    workflow.add_conditional_edges(
        "generate",
        route_after_generate,
        {
            "prioritize": "prioritize",
            "generate": "generate",
            END: END,
        },
    )

    # prioritize → conditional routing (proceed to publish or end)
    workflow.add_conditional_edges(
        "prioritize",
        route_after_prioritize,
        {
            "publish": "publish",
            END: END,
        },
    )

    # publish → END (terminal node)
    workflow.add_edge("publish", END)

    # Compile with checkpointer
    compiled = workflow.compile(checkpointer=checkpointer)

    logger.info("agent_graph_compiled", nodes=["ingest", "generate", "prioritize", "publish"])

    return compiled


async def run_agent(
    user_story_text: str = "",
    target_url: str | None = None,
    crawl_results=None,
    thread_id: str = "default",
) -> AgentState:
    """Execute the agent graph with the given inputs.

    Convenience function that creates the graph and runs it end-to-end
    with proper initial state.

    Args:
        user_story_text: The user story text to process.
        target_url: Optional target URL for crawl-based flow.
        crawl_results: Optional pre-computed crawl results.
        thread_id: Thread identifier for checkpointing.

    Returns:
        Final AgentState after graph execution completes.
    """
    graph = create_agent_graph()

    # Build initial state
    initial_state: AgentState = {
        "user_story_text": user_story_text,
        "target_url": target_url,
        "retrieved_docs": [],
        "test_scenarios": [],
        "site_map": None,
        "crawl_results": crawl_results,
        "plane_task_id": None,
        "plane_task_ids": [],
        "execution_status": "pending",
        "current_node": "start",
        "error_message": None,
        "retry_count": 0,
    }

    config = {"configurable": {"thread_id": thread_id}}

    logger.info(
        "agent_run_started",
        has_story=bool(user_story_text),
        has_url=bool(target_url),
        has_crawl_results=crawl_results is not None,
        thread_id=thread_id,
    )

    # Execute the graph
    final_state = await graph.ainvoke(initial_state, config=config)

    logger.info(
        "agent_run_completed",
        scenarios_generated=len(final_state.get("test_scenarios", [])),
        tasks_created=len(final_state.get("plane_task_ids", [])),
        final_node=final_state.get("current_node", "unknown"),
        has_error=bool(final_state.get("error_message")),
    )

    return final_state
