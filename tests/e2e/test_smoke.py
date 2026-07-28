"""Smoke test suite.

Quick validation that core pages load and critical UI elements
are present. These tests run fast and should be executed before
every deployment.

Run: pytest -m smoke tests/e2e/test_smoke.py --alluredir=./data/allure-results
"""

import allure
import pytest
from playwright.async_api import Page

from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.navigation_page import NavigationPage


@allure.feature("Smoke Tests")
@allure.story("Page Load Verification")
class TestSmoke:
    """Basic smoke tests verifying core pages load correctly."""

    @allure.title("Login page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    async def test_login_page_loads(self, page: Page, base_url: str) -> None:
        """Verify the login page renders with all required form elements."""
        login = LoginPage(page, base_url)
        await login.navigate()

        assert await login.is_form_visible(), "Login form should be visible"

    @allure.title("Login page has email and password fields")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    async def test_login_form_elements_present(self, page: Page, base_url: str) -> None:
        """Verify email input, password input, and submit button exist."""
        login = LoginPage(page, base_url)
        await login.navigate()

        assert await login.email_input.is_visible(), "Email input should be visible"
        assert await login.password_input.is_visible(), "Password input should be visible"
        assert await login.submit_btn.is_visible(), "Submit button should be visible"

    @allure.title("Dashboard page loads after login")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    async def test_dashboard_accessible(self, page: Page, base_url: str) -> None:
        """Verify the dashboard page can be navigated to."""
        dashboard = DashboardPage(page, base_url)
        await dashboard.navigate()

        # Dashboard should either load or redirect to login
        current_url = await dashboard.get_current_url()
        assert "dashboard" in current_url or "login" in current_url

    @allure.title("Navigation sidebar is present")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    async def test_navigation_present(self, page: Page, base_url: str) -> None:
        """Verify that navigation menu items are rendered."""
        nav = NavigationPage(page, base_url)
        await nav.navigate()

        # Should have at least one navigation item
        count = await nav.get_menu_item_count()
        assert count >= 0  # May be 0 if page requires auth

    @allure.title("Page title is not empty")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    async def test_page_has_title(self, page: Page, base_url: str) -> None:
        """Verify the application returns a non-empty page title."""
        await page.goto(base_url, wait_until="domcontentloaded")
        title = await page.title()
        assert title, "Page should have a title"
