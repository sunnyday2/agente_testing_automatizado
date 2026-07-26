"""Prioritize node for the LangGraph agent.

Re-evaluates and assigns final priorities to generated test scenarios
using LLM-based analysis of scenario content, coverage, and risk level.
"""

import json

from pydantic import BaseModel, Field

from src.agent.llm_provider import LLMProvider
from src.agent.prompts.priority_assignment import build_priority_prompt
from src.agent.state import AgentState, PriorityAssignment, TestScenario
from src.common.exceptions import LLMProviderError, LLMResponseParseError
from src.common.logging import get_logger

logger = get_logger(__name__)


class PriorityAssignmentList(BaseModel):
    """Expected output from the priority assignment LLM call."""

    priorities: list[PriorityAssignment] = Field(
        default_factory=list,
        description="List of priority assignments for each scenario",
    )


async def prioritize_node(state: AgentState) -> dict:
    """Assign final priorities to generated test scenarios.

    Uses the LLM to evaluate each scenario's importance based on
    business impact, security implications, and coverage criticality.

    If the LLM call fails, the original priorities from generation
    are preserved (graceful degradation).

    Args:
        state: Current agent state with test_scenarios populated.

    Returns:
        State update dict with updated test_scenarios and current_node.
    """
    scenarios = state.get("test_scenarios", [])

    if not scenarios:
        logger.warning("prioritize_node_skipped_no_scenarios")
        return {
            "test_scenarios": [],
            "current_node": "prioritize",
        }

    logger.info("prioritize_node_started", scenarios_count=len(scenarios))

    # Build story summary for context
    story_summary = state.get("user_story_text", "")[:300]
    if not story_summary and state.get("crawl_results"):
        story_summary = f"Site crawl from: {state['crawl_results'].site_map.start_url}"

    # Prepare scenarios for the prompt
    scenarios_for_prompt = [
        {
            "title": s.title,
            "description": s.description,
            "test_type": s.test_type,
            "tags": s.tags,
        }
        for s in scenarios
    ]

    system_prompt, user_prompt = build_priority_prompt(
        story_summary=story_summary,
        scenarios=scenarios_for_prompt,
    )

    provider = LLMProvider()

    try:
        result = await provider.generate_structured(
            prompt=user_prompt,
            output_model=PriorityAssignmentList,
            system_prompt=system_prompt,
        )

        # Apply priority assignments back to scenarios
        updated_scenarios = _apply_priorities(scenarios, result.priorities)

        logger.info(
            "prioritize_completed",
            p1_count=sum(1 for s in updated_scenarios if s.priority == "P1"),
            p2_count=sum(1 for s in updated_scenarios if s.priority == "P2"),
            p3_count=sum(1 for s in updated_scenarios if s.priority == "P3"),
        )

        return {
            "test_scenarios": updated_scenarios,
            "current_node": "prioritize",
        }

    except (LLMProviderError, LLMResponseParseError) as e:
        # Graceful degradation: keep original priorities
        logger.warning(
            "prioritize_failed_keeping_original_priorities",
            error=str(e),
        )
        return {
            "test_scenarios": scenarios,
            "current_node": "prioritize",
            "error_message": f"Priority assignment failed (using defaults): {e.message}",
        }


def _apply_priorities(
    scenarios: list[TestScenario],
    assignments: list[PriorityAssignment],
) -> list[TestScenario]:
    """Apply priority assignments back to scenario objects.

    Matches assignments to scenarios by title. Unmatched scenarios
    retain their original priority.

    Args:
        scenarios: Original list of test scenarios.
        assignments: Priority assignments from the LLM.

    Returns:
        Updated list of test scenarios with new priorities applied.
    """
    # Build lookup by normalized title
    assignment_map: dict[str, PriorityAssignment] = {
        a.scenario_title.strip().lower(): a for a in assignments
    }

    updated: list[TestScenario] = []
    for scenario in scenarios:
        normalized_title = scenario.title.strip().lower()
        assignment = assignment_map.get(normalized_title)

        if assignment:
            # Create updated scenario with new priority
            updated_scenario = scenario.model_copy(
                update={"priority": assignment.priority}
            )
            updated.append(updated_scenario)
        else:
            # Keep original priority
            updated.append(scenario)

    return updated
