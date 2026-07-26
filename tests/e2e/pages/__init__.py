"""Page Object Model classes for E2E tests.

Each class encapsulates interactions with a specific page or
component, exposing semantic methods instead of raw selectors.
"""

from tests.e2e.pages.base_page import BasePage
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.navigation_page import NavigationPage

__all__ = ["BasePage", "DashboardPage", "LoginPage", "NavigationPage"]
