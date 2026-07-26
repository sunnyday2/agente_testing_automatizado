"""Agent state definitions for the LangGraph state machine.

Defines the TypedDict used as the shared state across all graph nodes,
plus Pydantic models for structured output parsing from LLM calls.

The AgentState flows through:
    ingest → generate → prioritize → publish
"""

from typing import Literal, Optional

from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# --- Pydantic Output Models ---


class TestStep(BaseModel):
    """A single step within a test scenario."""

    action: str = Field(description="The user action to perform (e.g., 'Click login button')")
    expected_result: str = Field(description="The expected outcome after the action")
    selector_hint: str = Field(
        default="",
        description="Optional CSS/XPath selector hint for automation",
    )


class TestScenario(BaseModel):
    """A generated test scenario from a user story.

    Represents a single test case with preconditions, steps, and
    expected behavior. Used as the structured output from the LLM
    test generation node.
    """

    title: str = Field(description="Short descriptive title of the test scenario")
    description: str = Field(description="Detailed description of what is being tested")
    priority: Literal["P1", "P2", "P3"] = Field(
        default="P2",
        description="Test priority: P1=critical, P2=important, P3=nice-to-have",
    )
    test_type: Literal["smoke", "regression", "e2e"] = Field(
        default="regression",
        description="Category of the test",
    )
    preconditions: list[str] = Field(
        default_factory=list,
        description="Conditions that must be true before the test starts",
    )
    steps: list[TestStep] = Field(
        default_factory=list,
        description="Ordered list of test steps with actions and expectations",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization (e.g., 'login', 'auth', 'validation')",
    )
    story_id: str = Field(
        default="",
        description="Reference to the source user story ID",
    )


class TestGenerationResult(BaseModel):
    """Collection of test scenarios generated from a single user story."""

    scenarios: list[TestScenario] = Field(
        default_factory=list,
        description="List of generated test scenarios",
    )
    source_story_summary: str = Field(
        default="",
        description="Brief summary of the source user story",
    )
    coverage_notes: str = Field(
        default="",
        description="Notes about what aspects of the story are covered",
    )


class PriorityAssignment(BaseModel):
    """Priority assignment result from the LLM."""

    scenario_title: str = Field(description="Title of the scenario being prioritized")
    priority: Literal["P1", "P2", "P3"] = Field(description="Assigned priority level")
    rationale: str = Field(description="Reasoning for the priority assignment")


# --- Crawl Result Models ---


class PageElement(BaseModel):
    """An interactive element discovered on a page during crawling."""

    tag: str = Field(description="HTML tag name (e.g., 'button', 'input', 'a')")
    element_type: str = Field(
        default="",
        description="Element type attribute (e.g., 'submit', 'text', 'email')",
    )
    text: str = Field(default="", description="Visible text content of the element")
    selector: str = Field(description="CSS selector to locate this element")
    aria_label: str = Field(default="", description="Accessibility label if present")


class PageNode(BaseModel):
    """A discovered page in the site map."""

    url: str = Field(description="Full URL of the page")
    title: str = Field(default="", description="Page title from <title> tag")
    depth: int = Field(default=0, description="Navigation depth from start URL")
    elements: list[PageElement] = Field(
        default_factory=list,
        description="Interactive elements found on this page",
    )
    links: list[str] = Field(
        default_factory=list,
        description="Outgoing links discovered on this page",
    )
    screenshot_path: str = Field(
        default="",
        description="Path to the captured screenshot of this page",
    )


class SiteMap(BaseModel):
    """Complete site map from a crawl operation."""

    start_url: str = Field(description="The initial URL the crawl started from")
    pages: list[PageNode] = Field(
        default_factory=list,
        description="All pages discovered during the crawl",
    )
    total_pages: int = Field(default=0, description="Total number of pages discovered")
    max_depth_reached: int = Field(default=0, description="Maximum depth navigated")


class CrawlResults(BaseModel):
    """Full results from a site crawl operation."""

    site_map: SiteMap = Field(description="The discovered site structure")
    suggested_flows: list[str] = Field(
        default_factory=list,
        description="Suggested user flows identified from the site structure",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors encountered during crawling",
    )


# --- Agent State TypedDict ---


class AgentState(TypedDict):
    """Shared state for the LangGraph agent state machine.

    This state is passed through all graph nodes and accumulates
    data as the agent progresses through its workflow.

    Flow:
        1. ingest: Populates user_story_text and retrieved_docs
        2. generate: Produces test_scenarios from story + context
        3. prioritize: Assigns priorities to test_scenarios
        4. publish: Creates Plane.so tasks and sets plane_task_id
    """

    # Input
    user_story_text: str
    target_url: Optional[str]

    # RAG retrieval
    retrieved_docs: list[Document]

    # Generation output
    test_scenarios: list[TestScenario]

    # Site crawl results (from URL-based flow)
    site_map: Optional[SiteMap]
    crawl_results: Optional[CrawlResults]

    # Publishing
    plane_task_id: Optional[str]
    plane_task_ids: list[str]

    # Execution tracking
    execution_status: Literal["pending", "running", "passed", "failed"]
    current_node: str
    error_message: Optional[str]
    retry_count: int
