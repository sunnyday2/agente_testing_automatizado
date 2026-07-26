"""Plane.so API client for task management.

Provides async methods for creating issues, updating statuses,
and querying the QA task board in Plane.so.

Usage:
    from src.api.services.plane_client import PlaneClient

    client = PlaneClient()
    task_id = await client.create_issue(name="Test Login", priority="high")
    await client.update_status(task_id, status="FINISHED")
"""

from typing import Literal

import httpx

from src.common.exceptions import PlaneAPIError
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

STATE_GROUPS = {
    "TODO": "backlog",
    "DOING": "started",
    "FINISHED": "completed",
    "FAILED": "cancelled",
}


class PlaneClient:
    """Async HTTP client for the Plane.so API."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._base_url = self._settings.plane.base_url
        self._api_key = self._settings.plane.api_key
        self._workspace = self._settings.plane.workspace_slug
        self._project = self._settings.plane.project_id

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._workspace and self._project)

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return (
            f"{self._base_url}/api/v1/workspaces/{self._workspace}"
            f"/projects/{self._project}{path}"
        )

    async def create_issue(
        self,
        name: str,
        description_html: str = "",
        priority: str = "medium",
        labels: list[str] | None = None,
    ) -> str:
        """Create a new issue. Returns the issue UUID."""
        if not self.is_configured:
            logger.warning("plane_not_configured_skipping_create")
            return ""

        payload: dict = {"name": name, "priority": priority}
        if description_html:
            payload["description_html"] = description_html
        if labels:
            payload["labels"] = labels

        url = self._url("/issues/")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=self._headers())

        if response.status_code not in (200, 201):
            raise PlaneAPIError(
                endpoint="/issues/",
                status_code=response.status_code,
                response_body=response.text,
            )

        issue_id = response.json().get("id", "")
        logger.info("plane_issue_created", issue_id=issue_id, name=name)
        return issue_id

    async def update_status(
        self,
        issue_id: str,
        status: Literal["TODO", "DOING", "FINISHED", "FAILED"],
    ) -> None:
        """Update an issue's state."""
        if not self.is_configured:
            logger.warning("plane_not_configured_skipping_update")
            return

        state_id = await self._resolve_state_id(status)
        if not state_id:
            logger.error("plane_state_not_found", target_state=status)
            return

        url = self._url(f"/issues/{issue_id}/")
        payload = {"state": state_id}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(url, json=payload, headers=self._headers())

        if response.status_code not in (200, 204):
            raise PlaneAPIError(
                endpoint=f"/issues/{issue_id}/",
                status_code=response.status_code,
                response_body=response.text,
            )

        logger.info("plane_issue_status_updated", issue_id=issue_id, new_status=status)

    async def add_comment(self, issue_id: str, comment_html: str) -> None:
        """Add a comment to an issue."""
        if not self.is_configured:
            return

        url = self._url(f"/issues/{issue_id}/comments/")
        payload = {"comment_html": comment_html}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=self._headers())

        if response.status_code not in (200, 201):
            logger.warning("plane_comment_failed", issue_id=issue_id, status=response.status_code)

    async def get_issue(self, issue_id: str) -> dict | None:
        """Get issue details by ID."""
        if not self.is_configured:
            return None

        url = self._url(f"/issues/{issue_id}/")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=self._headers())
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning("plane_get_issue_failed", issue_id=issue_id, error=str(e))
        return None

    async def _resolve_state_id(self, state_name: str) -> str | None:
        """Resolve a state name to its UUID."""
        url = self._url("/states/")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=self._headers())

            if response.status_code != 200:
                return None

            data = response.json()
            states = data if isinstance(data, list) else data.get("results", [])

            for state in states:
                if state.get("name", "").upper() == state_name.upper():
                    return state.get("id")
                expected_group = STATE_GROUPS.get(state_name, "")
                if expected_group and state.get("group") == expected_group:
                    return state.get("id")

        except Exception as e:
            logger.warning("plane_state_resolution_failed", error=str(e))

        return None
