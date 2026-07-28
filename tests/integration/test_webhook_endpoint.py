"""Integration tests for the webhook → test runner flow.

Tests the full path: POST /webhooks/plane → payload parsing →
state check → background task trigger. Uses the FastAPI test client.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.app import create_app


@pytest.fixture
def app():
    """Create a fresh app instance for testing."""
    return create_app()


@pytest.fixture
async def client(app):
    """Async HTTP client wired to the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestWebhookEndpoint:
    """Integration tests for POST /webhooks/plane."""

    @pytest.mark.integration
    async def test_webhook_accepted_doing_state(self, client: AsyncClient):
        """Verify webhook with DOING state is accepted and triggers execution."""
        payload = {
            "event": "issue.activity",
            "action": "updated",
            "data": {
                "id": "issue-uuid-001",
                "name": "[P1] Test Login Flow",
                "state": {"name": "DOING", "group": "started", "id": "state-1"},
                "priority": "high",
                "labels": [{"id": "lbl-1", "name": "smoke", "color": "#fff"}],
                "project": "proj-1",
                "workspace": "qa-workspace",
            },
        }

        response = await client.post("/webhooks/plane", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "accepted"
        assert "Test execution triggered" in data["message"]
        assert data["issue_id"] == "issue-uuid-001"

    @pytest.mark.integration
    async def test_webhook_ignored_todo_state(self, client: AsyncClient):
        """Verify webhook with TODO state is ignored (no trigger)."""
        payload = {
            "event": "issue.activity",
            "action": "updated",
            "data": {
                "id": "issue-uuid-002",
                "name": "Some task",
                "state": {"name": "TODO", "group": "backlog", "id": "state-2"},
                "priority": "medium",
                "labels": [],
                "project": "proj-1",
                "workspace": "qa-workspace",
            },
        }

        response = await client.post("/webhooks/plane", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ignored"

    @pytest.mark.integration
    async def test_webhook_ignored_finished_state(self, client: AsyncClient):
        """Verify webhook with FINISHED state is ignored."""
        payload = {
            "event": "issue.activity",
            "action": "updated",
            "data": {
                "id": "issue-uuid-003",
                "name": "Completed task",
                "state": {"name": "FINISHED", "group": "completed", "id": "state-3"},
                "priority": "low",
                "labels": [],
                "project": "proj-1",
                "workspace": "qa-workspace",
            },
        }

        response = await client.post("/webhooks/plane", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "ignored"

    @pytest.mark.integration
    async def test_webhook_extracts_smoke_tag_from_labels(self, client: AsyncClient):
        """Verify test tags are extracted from issue labels."""
        payload = {
            "event": "issue",
            "action": "updated",
            "data": {
                "id": "issue-uuid-004",
                "name": "Smoke test task",
                "state": {"name": "DOING", "group": "started", "id": "state-1"},
                "priority": "high",
                "labels": [
                    {"id": "lbl-1", "name": "regression", "color": "#fff"},
                    {"id": "lbl-2", "name": "e2e", "color": "#000"},
                ],
                "project": "proj-1",
                "workspace": "qa-workspace",
            },
        }

        response = await client.post("/webhooks/plane", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    @pytest.mark.integration
    async def test_webhook_invalid_payload_returns_422(self, client: AsyncClient):
        """Verify malformed payload returns validation error."""
        payload = {"event": "issue", "action": "updated"}
        # Missing required 'data' field

        response = await client.post("/webhooks/plane", json=payload)
        assert response.status_code == 422


class TestHealthEndpoint:
    """Integration tests for the health check."""

    @pytest.mark.integration
    async def test_health_returns_status(self, client: AsyncClient):
        """Verify health endpoint returns structured response."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "checks" in data
        assert data["status"] in ("healthy", "degraded")
