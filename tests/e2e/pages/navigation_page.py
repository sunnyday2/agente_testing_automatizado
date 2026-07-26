"""Navigation Page Object Model.

Encapsulates interactions with the sidebar navigation menu
including collapse/expand, menu item selection, and mobile
hamburger toggle.
"""

import allure
from playwright.async_api import Page

from tests.e2e.pages.base_page import BasePage


class NavigationPage(BasePage):
    """Page Object for the sidebar navigation component.

    This is a component-level POM — it doesn't represent a full page
    but a reusable navigation section present on multiple pages.
    """

    URL_PATH = "/"

    def __init__(self, page: Page, base_url: str = "") -> None:
        super().__init__(page, base_url)
        # Sidebar structure
        self.sidebar = page.locator("[data-testid='sidebar'], nav[role='navigation']")
        self.collapse_btn = page.locator("[data-testid='sidebar-collapse']")
        self.expand_btn = page.locator("[data-testid='sidebar-expand']")
        self.hamburger_btn = page.locator("[data-testid='hamburger-menu']")

        # Menu items
        self.menu_items = page.locator("[data-testid='nav-item'], nav a")
        self.active_item = page.locator("[data-testid='nav-item'].active, nav a[aria-current='page']")

    @allure.step("Collapse sidebar")
    async def collapse(self) -> None:
        """Collapse the sidebar to icon-only view."""
        if await self.collapse_btn.is_visible():
            await self.collapse_btn.click()

    @allure.step("Expand sidebar")
    async def expand(self) -> None:
        """Expand the sidebar to show full labels."""
        if await self.expand_btn.is_visible():
            await self.expand_btn.click()

    @allure.step("Toggle mobile hamburger menu")
    async def toggle_mobile_menu(self) -> None:
        """Click the hamburger menu for mobile viewports."""
        await self.hamburger_btn.click()

    @allure.step("Navigate to menu item: {item_text}")
    async def navigate_to_item(self, item_text: str) -> None:
        """Click a navigation menu item by its visible text.

        Args:
            item_text: The text label of the menu item to click.
        """
        item = self.page.locator(
            f"[data-testid='nav-item']:has-text('{item_text}'), "
            f"nav a:has-text('{item_text}')"
        ).first
        await item.click()

    @allure.step("Check if sidebar is collapsed")
    async def is_collapsed(self) -> bool:
        """Check if the sidebar is in collapsed (icon-only) state."""
        # Check for collapsed class or narrow width
        sidebar_class = await self.sidebar.get_attribute("class") or ""
        return "collapsed" in sidebar_class or "narrow" in sidebar_class

    @allure.step("Get active menu item text")
    async def get_active_item_text(self) -> str:
        """Get the text of the currently active/highlighted menu item.

        Returns:
            Active item text, or empty string if none is active.
        """
        if await self.active_item.count() > 0:
            return (await self.active_item.first.text_content()) or ""
        return ""

    @allure.step("Get all menu item labels")
    async def get_menu_labels(self) -> list[str]:
        """Get the text labels of all navigation menu items.

        Returns:
            List of menu item text strings.
        """
        count = await self.menu_items.count()
        labels: list[str] = []
        for i in range(count):
            text = await self.menu_items.nth(i).text_content()
            if text and text.strip():
                labels.append(text.strip())
        return labels

    @allure.step("Count menu items")
    async def get_menu_item_count(self) -> int:
        """Get the number of visible navigation items."""
        return await self.menu_items.count()
