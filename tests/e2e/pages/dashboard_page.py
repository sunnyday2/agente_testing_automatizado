"""Dashboard Page Object Model.

Encapsulates interactions with the main dashboard including
widget management, navigation sidebar, and user profile access.
"""

import allure
from playwright.async_api import Page

from tests.e2e.pages.base_page import BasePage


class DashboardPage(BasePage):
    """Page Object for the main dashboard page."""

    URL_PATH = "/dashboard"

    def __init__(self, page: Page, base_url: str = "") -> None:
        super().__init__(page, base_url)
        # Layout elements
        self.sidebar = page.locator("[data-testid='sidebar']")
        self.main_content = page.locator("[data-testid='main-content']")
        self.header = page.locator("[data-testid='header']")

        # User profile
        self.user_avatar = page.locator("[data-testid='user-avatar']")
        self.user_menu = page.locator("[data-testid='user-menu']")
        self.logout_btn = page.locator("[data-testid='logout-btn']")

        # Widgets
        self.widgets_grid = page.locator("[data-testid='widgets-grid']")
        self.widget_items = page.locator("[data-testid='widget-item']")
        self.add_widget_btn = page.locator("[data-testid='add-widget']")

        # Notifications
        self.notification_bell = page.locator("[data-testid='notification-bell']")
        self.notification_count = page.locator("[data-testid='notification-count']")

    @allure.step("Verify dashboard is loaded")
    async def is_loaded(self) -> bool:
        """Check if the dashboard has fully loaded."""
        try:
            await self.main_content.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    @allure.step("Get widget count")
    async def get_widget_count(self) -> int:
        """Return the number of widgets currently displayed."""
        return await self.widget_items.count()

    @allure.step("Click add widget button")
    async def click_add_widget(self) -> None:
        """Open the widget catalog to add a new widget."""
        await self.add_widget_btn.click()

    @allure.step("Open user menu")
    async def open_user_menu(self) -> None:
        """Click the user avatar to open the profile dropdown."""
        await self.user_avatar.click()
        await self.user_menu.wait_for(state="visible", timeout=3000)

    @allure.step("Logout")
    async def logout(self) -> None:
        """Open user menu and click logout."""
        await self.open_user_menu()
        await self.logout_btn.click()

    @allure.step("Get notification count")
    async def get_notification_count(self) -> int:
        """Get the number shown on the notification badge.

        Returns:
            Notification count, or 0 if badge is not visible.
        """
        if await self.notification_count.is_visible():
            text = (await self.notification_count.text_content()) or "0"
            try:
                return int(text.strip())
            except ValueError:
                return 0
        return 0

    @allure.step("Check sidebar is visible")
    async def is_sidebar_visible(self) -> bool:
        """Check if the navigation sidebar is displayed."""
        return await self.sidebar.is_visible()

    @allure.step("Get page heading")
    async def get_heading(self) -> str:
        """Get the main heading text on the dashboard."""
        heading = self.page.locator("h1, [data-testid='page-heading']").first
        if await heading.is_visible():
            return (await heading.text_content()) or ""
        return ""
