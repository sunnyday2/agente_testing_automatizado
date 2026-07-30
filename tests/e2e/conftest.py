"""E2E test configuration and fixtures.

Provides browser lifecycle management, base URL configuration,
Allure integration with auto-screenshot on failure, and
configurable headless/browser settings.
"""

import os
from pathlib import Path

import allure
import pytest
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# Project root for resolving paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom CLI options for e2e tests."""
    parser.addoption(
        "--browser-name",
        action="store",
        default=os.getenv("TEST_BROWSER", "chromium"),
        choices=["chromium", "firefox", "webkit"],
        help="Browser engine to use for tests",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in headed mode (visible window)",
    )
    parser.addoption(
        "--slowmo",
        action="store",
        default=0,
        type=int,
        help="Slow down operations by specified milliseconds",
    )


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """Base URL for the application under test."""
    return request.config.getoption("--base-url")


@pytest.fixture(scope="session")
def browser_name(request: pytest.FixtureRequest) -> str:
    """Browser engine name."""
    return request.config.getoption("--browser-name")


@pytest.fixture(scope="session")
def is_headless(request: pytest.FixtureRequest) -> bool:
    """Whether to run in headless mode."""
    headed = request.config.getoption("--headed")
    env_headless = os.getenv("TEST_HEADLESS", "true").lower() == "true"
    return not headed and env_headless


@pytest.fixture(scope="session")
def slow_mo(request: pytest.FixtureRequest) -> int:
    """Slow motion delay in milliseconds."""
    return request.config.getoption("--slowmo")


@pytest.fixture(scope="session")
def browser_context_args() -> dict:
    """Default browser context arguments applied to all contexts.

    Matches the testing-standards steering rule for viewport and HTTPS.
    """
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
async def browser(browser_name: str, is_headless: bool, slow_mo: int):
    """Session-scoped browser instance.

    Launches the configured browser engine and closes it at the
    end of the test session.
    """
    async with async_playwright() as p:
        browser_type = getattr(p, browser_name)
        browser_instance = await browser_type.launch(
            headless=is_headless,
            slow_mo=slow_mo,
        )
        yield browser_instance
        await browser_instance.close()


@pytest.fixture
async def context(browser: Browser, browser_context_args: dict):
    """Test-scoped browser context with clean state.

    Creates a fresh context per test for isolation (separate cookies,
    storage, etc.). Closes after each test.
    """
    ctx = await browser.new_context(**browser_context_args)
    yield ctx
    await ctx.close()


@pytest.fixture
async def page(context: BrowserContext, base_url: str):
    """Test-scoped page instance.

    Creates a new page in the browser context and navigates to the
    base URL. Available to all e2e tests.
    """
    pg = await context.new_page()
    try:
        await pg.goto(base_url, wait_until="domcontentloaded", timeout=15000)
    except Exception:
        pass  # Some tests may override the starting page
    yield pg
    await pg.close()


@pytest.fixture(autouse=True)
async def capture_on_failure(request: pytest.FixtureRequest, page: Page):
    """Auto-capture screenshot on test failure and attach to Allure report.

    Runs after each test. If the test failed, captures a full-page
    screenshot and attaches it to the Allure report.
    """
    yield

    # After test execution: check if it failed
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        try:
            screenshot = await page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"failure_{request.node.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass  # Don't fail teardown if screenshot fails


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """Store test result on the item for the screenshot fixture."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
