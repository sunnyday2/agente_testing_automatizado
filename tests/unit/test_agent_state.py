"""Unit tests for agent state models and Pydantic schemas."""

import pytest

from src.agent.state import (
    AgentState,
    CrawlResults,
    PageElement,
    PageNode,
    PriorityAssignment,
    SiteMap,
    TestGenerationResult,
    TestScenario,
    TestStep,
)


class TestTestStep:
    """Tests for TestStep model."""

    @pytest.mark.unit
    def test_create_with_all_fields(self):
        step = TestStep(
            action="Click login button",
            expected_result="User is redirected to dashboard",
            selector_hint="button[type='submit']",
        )
        assert step.action == "Click login button"
        assert step.expected_result == "User is redirected to dashboard"
        assert step.selector_hint == "button[type='submit']"

    @pytest.mark.unit
    def test_create_with_defaults(self):
        step = TestStep(action="action", expected_result="result")
        assert step.selector_hint == ""


class TestTestScenario:
    """Tests for TestScenario model."""

    @pytest.mark.unit
    def test_create_full_scenario(self):
        scenario = TestScenario(
            title="Login with valid credentials",
            description="Verify successful login redirects to dashboard",
            priority="P1",
            test_type="smoke",
            preconditions=["User exists", "User is on login page"],
            steps=[
                TestStep(action="Enter email", expected_result="Email shown"),
                TestStep(action="Click submit", expected_result="Redirected"),
            ],
            tags=["login", "auth", "smoke"],
            story_id="US-001",
        )
        assert scenario.title == "Login with valid credentials"
        assert scenario.priority == "P1"
        assert len(scenario.steps) == 2
        assert "login" in scenario.tags

    @pytest.mark.unit
    def test_default_priority_is_p2(self):
        scenario = TestScenario(title="Test", description="Desc")
        assert scenario.priority == "P2"

    @pytest.mark.unit
    def test_default_test_type_is_regression(self):
        scenario = TestScenario(title="Test", description="Desc")
        assert scenario.test_type == "regression"

    @pytest.mark.unit
    def test_invalid_priority_rejected(self):
        with pytest.raises(Exception):  # Pydantic validation error
            TestScenario(title="Test", description="Desc", priority="P4")


class TestTestGenerationResult:
    """Tests for TestGenerationResult model."""

    @pytest.mark.unit
    def test_create_with_scenarios(self):
        result = TestGenerationResult(
            scenarios=[
                TestScenario(title="Test 1", description="Desc 1"),
                TestScenario(title="Test 2", description="Desc 2"),
            ],
            source_story_summary="Login story",
            coverage_notes="Covers happy path and error case",
        )
        assert len(result.scenarios) == 2
        assert result.source_story_summary == "Login story"

    @pytest.mark.unit
    def test_empty_scenarios_by_default(self):
        result = TestGenerationResult()
        assert result.scenarios == []


class TestPriorityAssignment:
    """Tests for PriorityAssignment model."""

    @pytest.mark.unit
    def test_create_assignment(self):
        assignment = PriorityAssignment(
            scenario_title="Login test",
            priority="P1",
            rationale="Core auth functionality",
        )
        assert assignment.priority == "P1"
        assert assignment.rationale == "Core auth functionality"


class TestSiteMapModels:
    """Tests for crawl-related state models."""

    @pytest.mark.unit
    def test_page_element_creation(self):
        elem = PageElement(
            tag="button",
            element_type="submit",
            text="Log In",
            selector="button[type='submit']",
            aria_label="Log in to account",
        )
        assert elem.tag == "button"
        assert elem.selector == "button[type='submit']"

    @pytest.mark.unit
    def test_page_node_with_elements(self):
        node = PageNode(
            url="https://example.com/login",
            title="Login Page",
            depth=1,
            elements=[
                PageElement(tag="input", selector="#email", element_type="email"),
            ],
            links=["https://example.com/register"],
        )
        assert node.url == "https://example.com/login"
        assert len(node.elements) == 1
        assert len(node.links) == 1

    @pytest.mark.unit
    def test_site_map_construction(self):
        site_map = SiteMap(
            start_url="https://example.com",
            pages=[
                PageNode(url="https://example.com", title="Home", depth=0),
                PageNode(url="https://example.com/about", title="About", depth=1),
            ],
            total_pages=2,
            max_depth_reached=1,
        )
        assert site_map.total_pages == 2
        assert site_map.max_depth_reached == 1

    @pytest.mark.unit
    def test_crawl_results_with_flows(self):
        results = CrawlResults(
            site_map=SiteMap(start_url="https://example.com", total_pages=0),
            suggested_flows=["Login flow", "Navigation flow"],
            errors=["Page /404 returned HTTP 404"],
        )
        assert len(results.suggested_flows) == 2
        assert len(results.errors) == 1
