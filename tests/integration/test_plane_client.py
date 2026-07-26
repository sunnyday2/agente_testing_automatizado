"""Integration tests for the Plane.so API client.

Tests the PlaneClient methods with mocked HTTP responses using respx.
"""

from unittest.mock import patch

import httpx
import pytest
import respx

from src.api.services.plane_client import PlaneClient
from src.common.exceptions import PlaneAPIError


@pytest.fixture
def mock_settings():
    """Provide mock settings for PlaneClient."""
    with patch("src.api.services.plane_client.get_settings") as mock:
        settings = mock.return_value
        settings.plane.base_url = "https://plane.test"
        settings.plane.api_key = "test-api-key"
        settings.plane.workspace_slug = "qa-workspace"
        settings.plane.project_id = "proj-123"
        yield settings


class TestPlaneClientCreateIssue:
    """Tests for issue creation."""

    @pytest.mark.integration
    @respx.mock
    async def test_create_issue_success(self, mock_settings):
        """Verify successful issue creation returns UUID."""
        url = (
            "https://plane.test/api/v1/workspaces/qa-workspace"
            "/projects/proj-123/issues/"
        )
        respx.post(url).mock(
            return_value=httpx.Response(
                201,
                json={"id": "issue-new-uuid", "name": "Test Issue"},
            )
        )

        client = PlaneClient()
        issue_id = await client.create_issue(
            name="[P1] Test Login Flow",
            priority="high",
            labels=["smoke"],
        )

        assert issue_id == "issue-new-uuid"

    @pytest.mark.integration
    @respx.mock
    async def test_create_issue_api_error(self, mock_settings):
        """Verify API error raises PlaneAPIError."""
        url = (
            "https://plane.test/api/v1/workspaces/qa-workspace"
            "/projects/proj-123/issues/"
        )
        respx.post(url).mock(
            return_value=httpx.Response(403, text="Forbidden")
        )

        client = PlaneClient()
        with pytest.raises(PlaneAPIError) as exc_info:
            await client.create_issue(name="Test", priority="medium")

        assert exc_info.value.details["status_code"] == 403


class TestPlaneClientUpdateStatus:
    """Tests for issue state updates."""

    @pytest.mark.integration
    @respx.mock
    async def test_update_status_resolves_state(self, mock_settings):
        """Verify status update resolves state name to ID and patches."""
        states_url = (
            "https://plane.test/api/v1/workspaces/qa-workspace"
            "/projects/proj-123/states/"
        )
        respx.get(states_url).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {"id": "state-1", "name": "TODO", "group": "backlog"},
                    {"id": "state-2", "name": "DOING", "group": "started"},
                    {"id": "state-3", "name": "FINISHED", "group": "completed"},
                    {"id": "state-4", "name": "FAILED", "group": "cancelled"},
                ],
            )
        )

        issue_url = (
            "https://plane.test/api/v1/workspaces/qa-workspace"
            "/projects/proj-123/issues/issue-001/"
        )
        patch_route = respx.patch(issue_url).mock(
            return_value=httpx.Response(200, json={"id": "issue-001"})
        )

        client = PlaneClient()
        await client.update_status("issue-001", "FINISHED")

        assert patch_route.called
        request_body = patch_route.calls[0].request.content
        assert b"state-3" in request_body

    @pytest.mark.integration
    @respx.mock
    async def test_update_status_state_not_found(self, mock_settings):
        """Verify graceful handling when state name is not found."""
        states_url = (
            "https://plane.test/api/v1/workspaces/qa-workspace"
            "/projects/proj-123/states/"
        )
        respx.get(states_url).mock(
            return_value=httpx.Response(200, json=[])
        )

        client = PlaneClient()
        # Should not raise, just log a warning
        await client.update_status("issue-001", "FINISHED")


class TestPlaneClientAddComment:
    """Tests for adding comments to issues."""

    @pytest.mark.integration
    @respx.mock
    async def test_add_comment_success(self, mock_settings):
        """Verify comment is posted successfully."""
        url = (
            "https://plane.test/api/v1/workspaces/qa-workspace"
            "/projects/proj-123/issues/issue-001/comments/"
        )
        comment_route = respx.post(url).mock(
            return_value=httpx.Response(201, json={"id": "comment-1"})
        )

        client = PlaneClient()
        await client.add_comment("issue-001", "<p>Tests passed!</p>")

        assert comment_route.called


class TestPlaneClientConfiguration:
    """Tests for client configuration checks."""

    @pytest.mark.integration
    def test_not_configured_without_api_key(self):
        """Verify is_configured returns False without API key."""
        with patch("src.api.services.plane_client.get_settings") as mock:
            mock.return_value.plane.base_url = "https://plane.test"
            mock.return_value.plane.api_key = ""
            mock.return_value.plane.workspace_slug = "ws"
            mock.return_value.plane.project_id = "proj"

            client = PlaneClient()
            assert client.is_configured is False

    @pytest.mark.integration
    async def test_create_issue_skipped_when_not_configured(self):
        """Verify operations are skipped when not configured."""
        with patch("src.api.services.plane_client.get_settings") as mock:
            mock.return_value.plane.base_url = "https://plane.test"
            mock.return_value.plane.api_key = ""
            mock.return_value.plane.workspace_slug = ""
            mock.return_value.plane.project_id = ""

            client = PlaneClient()
            result = await client.create_issue(name="Test")
            assert result == ""
