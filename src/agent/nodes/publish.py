"""Publish node for the LangGraph agent.

Creates tasks in Plane.so from generated test scenarios. Each test scenario
becomes a task on the QA board with appropriate labels, priority, and
description formatting.
"""

import httpx

from src.agent.state import AgentState, TestScenario
from src.common.exceptions import PlaneAPIError
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

# Plane.so priority mapping (Plane uses integer priorities)
PRIORITY_MAP = {
    "P1": 1,  # Urgent
    "P2": 2,  # High
    "P3": 3,  # Medium
}


async def publish_node(state: AgentState) -> dict:
    """Create Plane.so tasks from generated and prioritized test scenarios.

    Creates one task per test scenario in the configured project board.
    Tasks include formatted descriptions with steps, preconditions,
    and metadata.

    Args:
        state: Current agent state with test_scenarios populated.

    Returns:
        State update dict with plane_task_ids and current_node.
    """
    scenarios = state.get("test_scenarios", [])

    if not scenarios:
        logger.warning("publish_node_skipped_no_scenarios")
        return {
            "plane_task_ids": [],
            "current_node": "publish",
            "execution_status": "pending",
        }

    settings = get_settings()
    logger.info(
        "publish_node_started",
        scenarios_count=len(scenarios),
        workspace=settings.plane.workspace_slug,
        project=settings.plane.project_id,
    )

    # Skip if Plane.so is not configured
    if not settings.plane.api_key or not settings.plane.project_id:
        logger.warning("publish_skipped_plane_not_configured")
        return {
            "plane_task_ids": [],
            "current_node": "publish",
            "execution_status": "pending",
            "error_message": "Plane.so not configured — tasks not created",
        }

    created_ids: list[str] = []
    errors: list[str] = []

    async with httpx.AsyncClient(
        base_url=settings.plane.base_url,
        headers={
            "X-API-Key": settings.plane.api_key,
            "Content-Type": "application/json",
        },
        timeout=30.0,
    ) as client:
        for scenario in scenarios:
            try:
                task_id = await _create_task(client, settings, scenario)
                created_ids.append(task_id)
            except PlaneAPIError as e:
                logger.error(
                    "plane_task_creation_failed",
                    scenario_title=scenario.title,
                    error=e.message,
                )
                errors.append(f"{scenario.title}: {e.message}")

    logger.info(
        "publish_completed",
        created_count=len(created_ids),
        failed_count=len(errors),
    )

    error_msg = None
    if errors:
        error_msg = f"Some tasks failed to create: {'; '.join(errors[:5])}"

    return {
        "plane_task_ids": created_ids,
        "plane_task_id": created_ids[0] if created_ids else None,
        "current_node": "publish",
        "execution_status": "pending",
        "error_message": error_msg,
    }


async def _create_task(
    client: httpx.AsyncClient,
    settings,
    scenario: TestScenario,
) -> str:
    """Create a single Plane.so task from a test scenario.

    Args:
        client: Configured httpx async client.
        settings: Application settings with Plane.so config.
        scenario: The test scenario to create a task for.

    Returns:
        The created task ID.

    Raises:
        PlaneAPIError: If the API call fails.
    """
    description = _format_task_description(scenario)

    payload = {
        "name": f"[{scenario.priority}] {scenario.title}",
        "description_html": description,
        "priority": PRIORITY_MAP.get(scenario.priority, 2),
        "labels": scenario.tags[:5],  # Plane.so may limit labels
        "state": "TODO",
    }

    endpoint = (
        f"/api/v1/workspaces/{settings.plane.workspace_slug}"
        f"/projects/{settings.plane.project_id}/issues/"
    )

    response = await client.post(endpoint, json=payload)

    if response.status_code not in (200, 201):
        raise PlaneAPIError(
            endpoint=endpoint,
            status_code=response.status_code,
            response_body=response.text,
        )

    data = response.json()
    task_id = data.get("id", "")

    logger.info(
        "plane_task_created",
        task_id=task_id,
        title=scenario.title,
        priority=scenario.priority,
    )

    return task_id


def _format_task_description(scenario: TestScenario) -> str:
    """Format a test scenario into an HTML description for Plane.so.

    Args:
        scenario: The test scenario to format.

    Returns:
        HTML-formatted description string.
    """
    parts: list[str] = []

    parts.append(f"<h3>{scenario.title}</h3>")
    parts.append(f"<p>{scenario.description}</p>")

    # Metadata
    parts.append(f"<p><strong>Type:</strong> {scenario.test_type} | ")
    parts.append(f"<strong>Priority:</strong> {scenario.priority} | ")
    parts.append(f"<strong>Story:</strong> {scenario.story_id or 'N/A'}</p>")

    # Preconditions
    if scenario.preconditions:
        parts.append("<h4>Preconditions</h4><ul>")
        for pre in scenario.preconditions:
            parts.append(f"<li>{pre}</li>")
        parts.append("</ul>")

    # Steps
    if scenario.steps:
        parts.append("<h4>Test Steps</h4><ol>")
        for step in scenario.steps:
            parts.append(
                f"<li><strong>Action:</strong> {step.action}<br/>"
                f"<strong>Expected:</strong> {step.expected_result}"
            )
            if step.selector_hint:
                parts.append(f"<br/><code>Selector: {step.selector_hint}</code>")
            parts.append("</li>")
        parts.append("</ol>")

    # Tags
    if scenario.tags:
        tags_str = ", ".join(f"<code>{tag}</code>" for tag in scenario.tags)
        parts.append(f"<p><strong>Tags:</strong> {tags_str}</p>")

    return "\n".join(parts)
