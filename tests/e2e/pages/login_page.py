"""Login Page Object Model.

Encapsulates all interactions with the login page including
authentication, validation error checks, and navigation to
the password reset flow.
"""

import allure
from playwright.async_api import Page

from tests.e2e.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for the login/authentication page."""

    URL_PATH = "/login"

    def __init__(self, page: Page, base_url: str = "") -> None:
        super().__init__(page, base_url)
        # Locators defined as instance properties (data-testid preferred)
        self.email_input = page.locator("[data-testid='email']")
        self.password_input = page.locator("[data-testid='password']")
        self.submit_btn = page.locator("[data-testid='login-submit']")
        self.error_message = page.locator("[data-testid='login-error']")
        self.forgot_password_link = page.locator("a[href*='forgot'], [data-testid='forgot-password']")
        self.remember_me_checkbox = page.locator("[data-testid='remember-me']")

    @allure.step("Login with email: {email}")
    async def login(self, email: str, password: str) -> "LoginPage":
        """Fill credentials and submit the login form.

        Args:
            email: User email address.
            password: User password.

        Returns:
            Self for chaining or further assertions.
        """
        await self.email_input.fill(email)
        await self.password_input.fill(password)
        await self.submit_btn.click()
        return self

    @allure.step("Check if login form is displayed")
    async def is_form_visible(self) -> bool:
        """Verify the login form elements are visible."""
        email_visible = await self.email_input.is_visible()
        password_visible = await self.password_input.is_visible()
        submit_visible = await self.submit_btn.is_visible()
        return email_visible and password_visible and submit_visible

    @allure.step("Get error message text")
    async def get_error_text(self) -> str:
        """Get the displayed error message text.

        Returns:
            Error message string, or empty if no error shown.
        """
        if await self.error_message.is_visible():
            return (await self.error_message.text_content()) or ""
        return ""

    @allure.step("Check if submit button is enabled")
    async def is_submit_enabled(self) -> bool:
        """Check whether the login submit button is clickable."""
        return await self.submit_btn.is_enabled()

    @allure.step("Click forgot password link")
    async def click_forgot_password(self) -> None:
        """Navigate to the password reset flow."""
        await self.forgot_password_link.click()

    @allure.step("Toggle remember me checkbox")
    async def toggle_remember_me(self, check: bool = True) -> None:
        """Check or uncheck the remember me option."""
        if check:
            await self.remember_me_checkbox.check()
        else:
            await self.remember_me_checkbox.uncheck()
