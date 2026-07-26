"""Webhook endpoint for Plane.so task status changes.

Receives webhook events from Plane.so when issue states change.
When an issue transitions to "DOING", triggers the test execution
pipeline as a background task.

Endpoint:
    POST /webhooks/plane
"""

from fastapi import APIRouter, BackgroundTasks, Request

from src.api.middleware.webhook_validator import validate_webhook_signature
from src.api.schemas.webhook import PlaneWebhookPayload, WebhookResponse
from src.common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# States that trigger test execution
TRIGGER_STATES = {"doing", "in progress", "in_progress", "started"}


@router.post(
    "/webhooks/plane",
    response_model=WebhookResponse,
    status_code=200,
)
async def receive_plane_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> WebhookResponse:
    """Receive and process a Plane.so webhook event.

    Validates the signature, parses the payload, and triggers test
    execution if the issue moved to a DOING-like state.

    Returns 200 immediately and processes async to avoid timeout.
    """
    # Validate webhook signature
    await validate_webhook_signature(request)

    # Parse the payload
    body = await request.json()
    payload = PlaneWebhookPayload.model_validate(body)

    logger.info(
        "webhook_received",
        event=payload.event,
        action=payload.action,
        issue_id=payload.data.id,
        issue_name=payload.data.name,
        state=payload.data.state.name,
    )

    # Check if this is a state transition we care about
    current_state = payload.data.state.name.lower()
    state_group = payload.data.state.group.lower()

    should_trigger = (
        current_state in TRIGGER_STATES
        or state_group == "started"
    )

    if not should_trigger:
        logger.info(
            "webhook_ignored_state_not_trigger",
            state=payload.data.state.name,
            group=state_group,
        )
        return WebhookResponse(
            status="ignored",
            message=f"State '{payload.data.state.name}' does not trigger execution",
            issue_id=payload.data.id,
        )

    # Extract test metadata from the issue
    test_tags = _extract_test_tags(payload)

    # Queue test execution as a background task
    background_tasks.add_task(
        _trigger_test_execution,
        issue_id=payload.data.id,
        issue_name=payload.data.name,
        priority=payload.data.priority,
        tags=test_tags,
    )

    logger.info(
        "webhook_accepted_triggering_tests",
        issue_id=payload.data.id,
        issue_name=payload.data.name,
        tags=test_tags,
    )

    return WebhookResponse(
        status="accepted",
        message=f"Test execution triggered for: {payload.data.name}",
        task_id=payload.data.id,
        issue_id=payload.data.id,
    )


def _extract_test_tags(payload: PlaneWebhookPayload) -> list[str]:
    """Extract test execution tags from issue labels.

    Maps Plane.so labels to pytest markers for selective test execution.

    Args:
        payload: The webhook payload.

    Returns:
        List of test tags/markers to run.
    """
    tags: list[str] = []

    for label in payload.data.labels:
        label_name = label.name.lower()
        # Map common labels to pytest markers
        if label_name in ("smoke", "regression", "e2e"):
            tags.append(label_name)
        elif "smoke" in label_name:
            tags.append("smoke")
        elif "regression" in label_name:
            tags.append("regression")

    # Default to smoke if no specific tags found
    if not tags:
        tags.append("smoke")

    return tags


async def _trigger_test_execution(
    issue_id: str,
    issue_name: str,
    priority: str,
    tags: list[str],
) -> None:
    """Background task to trigger test execution.

    This will be fully wired in Task 13 when test_runner service
    is implemented. For now, logs the intent.

    Args:
        issue_id: The Plane.so issue ID.
        issue_name: The issue title.
        priority: Issue priority level.
        tags: Pytest markers/tags to run.
    """
    logger.info(
        "test_execution_triggered",
        issue_id=issue_id,
        issue_name=issue_name,
        priority=priority,
        tags=tags,
    )

    # TODO: Wire to test_runner service (Task 13)
    # from src.api.services.test_runner import TestRunner
    # runner = TestRunner()
    # result = await runner.run(tags=tags)
    # ... update Plane.so status based on result
