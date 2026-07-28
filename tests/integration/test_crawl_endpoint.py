"""Integration tests for the crawl → test generation flow.

Tests the POST /crawl endpoint with mocked Playwright to verify
the request parsing, crawl orchestration, and response format.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.agent.state import CrawlResults, PageElement, PageNode, SiteMap
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


def _mock_crawl_results(start_url: str = "https://example.com") -> CrawlResults:
    """Build a mock CrawlResults object for testing."""
    return CrawlResults(
        site_map=SiteMap(
            start_url=start_url,
            pages=[
                PageNode(
                    url=start_url,
                    title="Home Page",
                    depth=0,
                    elements=[
                        PageElement(tag="button", selector="#login-btn", text="Login"),
                        PageElement(tag="input", selector="#search", element_type="text"),
                    ],
                    links=[f"{start_url}/about", f"{start_url}/login"],
                ),
                PageNode(
                    url=f"{start_url}/login",
                    title="Login",
                    depth=1,
                    elements=[
                        PageElement(tag="input", selector="#email", element_type="email"),
                        PageElement(tag="input", selector="#password", element_type="password"),
                        PageElement(tag="button", selector="#submit", text="Sign In"),
                    ],
                    links=[],
                ),
            ],
            total_pages=2,
            max_depth_reached=1,
        ),
        suggested_flows=["Authentication flow: login page → dashboard"],
        errors=[],
    )


class TestCrawlEndpoint:
    """Integration tests for POST /crawl."""

    @pytest.mark.integration
    @patch("src.api.routes.crawl.CrawlerEngine")
    async def test_crawl_returns_completed_response(
        self, mock_engine_class, client: AsyncClient
    ):
        """Verify successful crawl returns completed status with page data."""
        mock_engine = AsyncMock()
        mock_engine.crawl.return_value = _mock_crawl_results()
        mock_engine_class.return_value = mock_engine

        response = await client.post(
            "/crawl",
            json={
                "url": "https://example.com",
                "max_depth": 2,
                "max_pages": 10,
                "generate_tests": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["total_pages"] == 2
        assert data["max_depth_reached"] == 1
        assert len(data["pages"]) == 2
        assert data["pages"][0]["title"] == "Home Page"
        assert data["pages"][1]["elements_count"] == 3
        assert "Authentication flow" in data["suggested_flows"][0]

    @pytest.mark.integration
    @patch("src.api.routes.crawl.CrawlerEngine")
    async def test_crawl_with_errors_returns_partial(
        self, mock_engine_class, client: AsyncClient
    ):
        """Verify crawl with errors returns partial status."""
        results = _mock_crawl_results()
        results.errors = ["Failed to load /broken: HTTP 500"]
        mock_engine = AsyncMock()
        mock_engine.crawl.return_value = results
        mock_engine_class.return_value = mock_engine

        response = await client.post(
            "/crawl",
            json={"url": "https://example.com", "generate_tests": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "partial"
        assert len(data["errors"]) == 1

    @pytest.mark.integration
    @patch("src.api.routes.crawl.CrawlerEngine")
    async def test_crawl_failure_returns_failed(
        self, mock_engine_class, client: AsyncClient
    ):
        """Verify crawl exception returns failed status."""
        mock_engine = AsyncMock()
        mock_engine.crawl.side_effect = Exception("Connection refused")
        mock_engine_class.return_value = mock_engine

        response = await client.post(
            "/crawl",
            json={"url": "https://unreachable.test", "generate_tests": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "Connection refused" in data["errors"][0]

    @pytest.mark.integration
    async def test_crawl_invalid_url_returns_422(self, client: AsyncClient):
        """Verify invalid URL returns validation error."""
        response = await client.post(
            "/crawl",
            json={"url": "not-a-valid-url", "max_depth": 2},
        )
        assert response.status_code == 422

    @pytest.mark.integration
    async def test_crawl_depth_out_of_range_returns_422(self, client: AsyncClient):
        """Verify max_depth > 10 is rejected."""
        response = await client.post(
            "/crawl",
            json={"url": "https://example.com", "max_depth": 15},
        )
        assert response.status_code == 422
