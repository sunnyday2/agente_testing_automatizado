"""Unit tests for API schemas and service models."""

import pytest
from pydantic import ValidationError

from src.api.schemas.common import (
    ErrorResponse,
    GenerationSummary,
    PaginatedResponse,
    SuccessResponse,
    TaskStatusResponse,
)
from src.api.schemas.crawl import CrawlRequest, CrawlResponse
from src.api.schemas.webhook import (
    PlaneWebhookPayload,
    WebhookIssueData,
    WebhookIssueState,
    WebhookResponse,
)


class TestCommonSchemas:
    """Tests for common response schemas."""

    @pytest.mark.unit
    def test_success_response_defaults(self):
        resp = SuccessResponse(message="Done")
        assert resp.status == "success"
        assert resp.message == "Done"
        assert resp.data == {}

    @pytest.mark.unit
    def test_error_response_fields(self):
        resp = ErrorResponse(
            error="TestError",
            message="Something failed",
            details={"key": "value"},
        )
        assert resp.error == "TestError"
        assert resp.details["key"] == "value"

    @pytest.mark.unit
    def test_paginated_response_total_pages(self):
        resp = PaginatedResponse(items=[], total=55, page=1, page_size=20)
        assert resp.total_pages == 3

    @pytest.mark.unit
    def test_paginated_response_has_next(self):
        resp = PaginatedResponse(items=[], total=100, page=1, page_size=20, has_next=True)
        assert resp.has_next is True

    @pytest.mark.unit
    def test_task_status_response(self):
        resp = TaskStatusResponse(
            task_id="abc-123",
            status="running",
            progress=0.5,
        )
        assert resp.task_id == "abc-123"
        assert resp.status == "running"
        assert resp.progress == 0.5

    @pytest.mark.unit
    def test_generation_summary(self):
        summary = GenerationSummary(
            scenarios_generated=5,
            tasks_created=5,
            source_type="user_story",
            source_identifier="US-001",
            priority_breakdown={"P1": 2, "P2": 2, "P3": 1},
        )
        assert summary.scenarios_generated == 5
        assert summary.source_type == "user_story"


class TestWebhookSchemas:
    """Tests for webhook payload models."""

    @pytest.mark.unit
    def test_parse_full_webhook_payload(self):
        payload = PlaneWebhookPayload(
            event="issue.activity",
            action="updated",
            data=WebhookIssueData(
                id="issue-uuid-123",
                name="Test Login Flow",
                state=WebhookIssueState(name="DOING", group="started"),
                priority="high",
                labels=[],
            ),
        )
        assert payload.event == "issue.activity"
        assert payload.data.state.name == "DOING"
        assert payload.data.state.group == "started"

    @pytest.mark.unit
    def test_webhook_response_accepted(self):
        resp = WebhookResponse(
            status="accepted",
            message="Test triggered",
            task_id="task-123",
            issue_id="issue-123",
        )
        assert resp.status == "accepted"

    @pytest.mark.unit
    def test_webhook_response_ignored(self):
        resp = WebhookResponse(status="ignored", message="State not trigger")
        assert resp.task_id == ""

    @pytest.mark.unit
    def test_webhook_payload_extra_fields_allowed(self):
        """Plane.so may send additional fields not in our schema."""
        payload = PlaneWebhookPayload(
            event="issue",
            action="created",
            data=WebhookIssueData(
                id="id-1",
                name="Issue",
                state=WebhookIssueState(name="TODO", group="backlog"),
            ),
            extra_unknown_field="should not fail",
        )
        assert payload.event == "issue"


class TestCrawlSchemas:
    """Tests for crawl request/response schemas."""

    @pytest.mark.unit
    def test_crawl_request_defaults(self):
        req = CrawlRequest(url="https://example.com")
        assert req.max_depth == 3
        assert req.max_pages == 50
        assert req.extract_elements is True
        assert req.generate_tests is True
        assert req.browser == "chromium"

    @pytest.mark.unit
    def test_crawl_request_validation_depth_range(self):
        """Verify max_depth is validated within range."""
        with pytest.raises(ValidationError):
            CrawlRequest(url="https://example.com", max_depth=0)
        with pytest.raises(ValidationError):
            CrawlRequest(url="https://example.com", max_depth=11)

    @pytest.mark.unit
    def test_crawl_request_validation_url(self):
        """Verify URL must be valid."""
        with pytest.raises(ValidationError):
            CrawlRequest(url="not-a-url")

    @pytest.mark.unit
    def test_crawl_response_completed(self):
        resp = CrawlResponse(
            status="completed",
            start_url="https://example.com",
            total_pages=5,
            max_depth_reached=2,
        )
        assert resp.status == "completed"
        assert resp.total_pages == 5

    @pytest.mark.unit
    def test_crawl_response_failed(self):
        resp = CrawlResponse(
            status="failed",
            start_url="https://example.com",
            errors=["Connection refused"],
        )
        assert resp.status == "failed"
        assert len(resp.errors) == 1
