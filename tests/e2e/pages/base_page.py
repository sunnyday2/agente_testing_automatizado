"""Base Page Object Model class.

Provides common utilities for all page objects: navigation, waiting,
element interactions, and assertion helpers. All POM classes should
inherit from BasePage.

Usage:
    from tests.e2e.pages.base_page import BasePage

    class LoginPage(BasePage):
        URL_PATH = "/login"

        def __init__(self, page: Page, base_url: str = ""):
            super().__init__(page, base_url)
            self.email_input = page.locator("[data-testid='email']")
            self.password_input = page.locator("[data-testid='password']")
            self.submit_btn = page.locator("[data-testid='login-submit']")

        async def login(self, email: str, password: str):
            await self.email_input.fill(email)
            await self.password_input.fill(password)
            await self.submit_btn.click()
"""

import allure
from playwright.async_api import Locator, Page


class BasePage:
    """Base class for all Page Object Model pages.

    Subclasses should:
    - Set URL_PATH class variable
    - Define locators as instance properties in __init__
    - Expose semantic methods (e.g., login, submit_form) not raw selectors
    """

    URL_PATH: str = "/"
    """Relative path for this page (override in subclasses)."""

    def __init__(self, page: Page, base_url: str = "") -> None:
        """Initialize with a Playwright page and optional base URL.

        Args:
            page: Playwright Page instance.
            base_url: Application base URL for navigation.
        """
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    def url(self) -> str:
        """Full URL for this page."""
        return f"{self.base_url}{self.URL_PATH}"

    # --- Navigation ---

    async def navigate(self) -> "BasePage":
        """Navigate to this page's URL. Returns self for chaining."""
        with allure.step(f"Navigate to {self.URL_PATH}"):
            await self.page.goto(self.url, wait_until="domcontentloaded")
        return self

    async def navigate_to(self, path: str) -> None:
        """Navigate to a specific path relative to base URL."""
        url = f"{self.base_url}{path}"
        await self.page.goto(url, wait_until="domcontentloaded")

    async def reload(self) -> None:
        """Reload the current page."""
        await self.page.reload(wait_until="domcontentloaded")

    # --- Element Interactions ---

    async def click(self, selector: str) -> None:
        """Click an element by selector."""
        with allure.step(f"Click: {selector}"):
            await self.page.locator(selector).click()

    async def fill(self, selector: str, value: str) -> None:
        """Fill a text input field by selector."""
        with allure.step(f"Fill '{selector}' with value"):
            await self.page.locator(selector).fill(value)

    async def select_option(self, selector: str, value: str) -> None:
        """Select an option in a dropdown by selector."""
        with allure.step(f"Select '{value}' in {selector}"):
            await self.page.locator(selector).select_option(value)

    async def check(self, selector: str) -> None:
        """Check a checkbox by selector."""
        await self.page.locator(selector).check()

    async def uncheck(self, selector: str) -> None:
        """Uncheck a checkbox by selector."""
        await self.page.locator(selector).uncheck()

    # --- Waiting ---

    async def wait_for_visible(self, selector: str, timeout: int = 5000) -> Locator:
        """Wait for an element to become visible.

        Returns the Locator for further interaction.
        """
        locator = self.page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        return locator

    async def wait_for_hidden(self, selector: str, timeout: int = 5000) -> None:
        """Wait for an element to become hidden."""
        await self.page.locator(selector).wait_for(state="hidden", timeout=timeout)

    async def wait_for_url(self, url_pattern: str, timeout: int = 10000) -> None:
        """Wait for the page URL to match a pattern (glob)."""
        await self.page.wait_for_url(url_pattern, timeout=timeout)

    async def wait_for_load(self) -> None:
        """Wait for the page to reach domcontentloaded state."""
        await self.page.wait_for_load_state("domcontentloaded")

    # --- Assertions / Queries ---

    async def is_visible(self, selector: str) -> bool:
        """Check if an element is currently visible."""
        return await self.page.locator(selector).is_visible()

    async def is_enabled(self, selector: str) -> bool:
        """Check if an element is enabled (not disabled)."""
        return await self.page.locator(selector).is_enabled()

    async def get_text(self, selector: str) -> str:
        """Get the text content of an element."""
        return (await self.page.locator(selector).text_content()) or ""

    async def get_value(self, selector: str) -> str:
        """Get the value of an input element."""
        return await self.page.locator(selector).input_value()

    async def get_attribute(self, selector: str, attribute: str) -> str | None:
        """Get an attribute value from an element."""
        return await self.page.locator(selector).get_attribute(attribute)

    async def count(self, selector: str) -> int:
        """Count the number of elements matching a selector."""
        return await self.page.locator(selector).count()

    # --- Page State ---

    async def get_title(self) -> str:
        """Get the page title."""
        return await self.page.title()

    async def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.page.url

    async def take_screenshot(self, name: str = "screenshot") -> bytes:
        """Capture a screenshot and attach to Allure.

        Args:
            name: Name for the Allure attachment.

        Returns:
            Screenshot bytes.
        """
        screenshot = await self.page.screenshot(full_page=True)
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
        return screenshot
