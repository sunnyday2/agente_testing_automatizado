"""Plane.so webhook payload models.

Defines Pydantic models for validating and parsing incoming webhook
events from Plane.so. Handles issue state transitions that trigger
test execution.

Plane.so webhook payload structure:
    {
        "event": "issue.activity",
        "action": "updated",
        "data": {
            "id": "uuid",
            "name": "Test scenario title",
            "state": { "name": "DOING", "group": "started" },
            "priority": "high",
            "labels": [...],
            "project": "project-id",
            "workspace": "workspace-slug",
            ...
        }
    }
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class WebhookIssueState(BaseModel):
    """Plane.so issue state within a webhook payload."""

    name: str = Field(description="State display name (e.g., 'DOING', 'TODO')")
    group: str = Field(
        default="",
        description="State group (e.g., 'started', 'unstarted', 'completed', 'cancelled')",
    )
    id: str = Field(default="", description="State UUID")
    color: str = Field(default="", description="State color hex code")


class WebhookIssueLabel(BaseModel):
    """A label attached to an issue."""

    id: str = Field(default="", description="Label UUID")
    name: str = Field(default="", description="Label display name")
    color: str = Field(default="", description="Label color hex code")


class WebhookIssueData(BaseModel):
    """Issue data within a Plane.so webhook event.

    Contains the relevant fields for triggering test execution
    when a task transitions to the DOING state.
    """

    id: str = Field(description="Issue UUID")
    name: str = Field(description="Issue title/name")
    state: WebhookIssueState = Field(description="Current issue state")
    priority: str = Field(default="none", description="Issue priority level")
    labels: list[WebhookIssueLabel] = Field(
        default_factory=list,
        description="Labels attached to the issue",
    )
    project: str = Field(default="", description="Project UUID")
    workspace: str = Field(default="", description="Workspace slug")
    description_html: str = Field(default="", description="Issue description HTML")
    sequence_id: int = Field(default=0, description="Issue sequence number")
    assignees: list[str] = Field(
        default_factory=list,
        description="List of assignee UUIDs",
    )

    class Config:
        extra = "allow"  # Allow additional fields from Plane.so


class PlaneWebhookPayload(BaseModel):
    """Top-level Plane.so webhook payload.

    This is the complete structure received on POST /webhooks/plane.
    """

    event: str = Field(
        description="Event type (e.g., 'issue.activity', 'issue')"
    )
    action: str = Field(
        description="Action performed (e.g., 'updated', 'created', 'deleted')"
    )
    data: WebhookIssueData = Field(description="Issue data payload")

    class Config:
        extra = "allow"


class WebhookResponse(BaseModel):
    """Response returned after processing a webhook event."""

    status: Literal["accepted", "ignored", "error"] = Field(
        description="Processing status"
    )
    message: str = Field(default="", description="Human-readable status message")
    task_id: str = Field(default="", description="ID of the triggered task, if any")
    issue_id: str = Field(default="", description="The Plane.so issue ID processed")
