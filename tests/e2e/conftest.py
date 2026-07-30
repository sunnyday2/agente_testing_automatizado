"""E2E test configuration and fixtures.

Uses pytest-playwright which provides:
  --base-url, --headed, --browser-name, --slowmo
  + browser, context, page fixtures automatically.

This conftest only adds:
  - Allure screenshot capture on failure
  - Browser context configuration (viewport, HTTPS)
"""

import os

import allure
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Override default browser context args with project defaults."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(autouse=True)
def capture_on_failure(request: pytest.FixtureRequest, page: Page):
    """Auto-capture screenshot on test failure and attach to Allure report."""
    yield

    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        try:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"failure_{request.node.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item):
    """Store test result on the item for the screenshot fixture."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
