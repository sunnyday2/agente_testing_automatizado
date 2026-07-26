"""Prompt templates for test scenario priority assignment.

Used by the prioritize node to re-evaluate and assign final priorities
to generated test scenarios based on risk, coverage, and business impact.
"""

SYSTEM_PROMPT = """You are a senior QA lead responsible for test prioritization. \
Your job is to assign the correct priority to each test scenario based on:

- **P1 (Critical):** Blocks release. Covers core functionality that must work. \
Login, payment, data integrity, security. If this fails, users cannot use the product.
- **P2 (Important):** Key functionality for user experience. Forms, navigation, \
CRUD operations. Failure degrades experience but has workarounds.
- **P3 (Nice-to-have):** Edge cases, cosmetic checks, rare user paths. Can be \
deferred without impacting release decisions.

Rules:
1. At least 20% of scenarios should be P1.
2. Consider the acceptance criteria severity — data loss risks are always P1.
3. Security-related scenarios (auth, access control) are always P1 or P2.
4. UI polish and cosmetic checks are P3.
5. Provide a brief rationale for each assignment.
6. Respond ONLY with valid JSON matching the provided schema."""

USER_PROMPT_TEMPLATE = """Review and assign priorities to the following test scenarios.

## Source User Story Summary
{story_summary}

## Scenarios to Prioritize
{scenarios_text}

For each scenario, provide:
- scenario_title: exact title of the scenario
- priority: P1, P2, or P3
- rationale: one sentence explaining why

Respond with a JSON object containing a "priorities" array of PriorityAssignment objects."""


class PriorityAssignmentResult:
    """Container for the expected output schema description."""

    schema_description = """{
  "priorities": [
    {
      "scenario_title": "string",
      "priority": "P1|P2|P3",
      "rationale": "string"
    }
  ]
}"""


def build_priority_prompt(
    story_summary: str,
    scenarios: list[dict],
) -> tuple[str, str]:
    """Build the complete prompt pair for priority assignment.

    Args:
        story_summary: Brief summary of the source user story.
        scenarios: List of scenario dicts with title and description.

    Returns:
        Tuple of (system_prompt, user_prompt) ready for the LLM.
    """
    scenarios_text = ""
    for i, scenario in enumerate(scenarios, 1):
        title = scenario.get("title", f"Scenario {i}")
        description = scenario.get("description", "")
        test_type = scenario.get("test_type", "regression")
        tags = ", ".join(scenario.get("tags", []))
        scenarios_text += (
            f"\n### {i}. {title}\n"
            f"- Description: {description}\n"
            f"- Type: {test_type}\n"
            f"- Tags: {tags}\n"
        )

    user = USER_PROMPT_TEMPLATE.format(
        story_summary=story_summary,
        scenarios_text=scenarios_text,
    )

    return SYSTEM_PROMPT, user
