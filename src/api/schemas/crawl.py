"""Crawl request and response schemas.

Defines Pydantic models for the POST /crawl endpoint, including
the request configuration and the response with crawl results summary.
"""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class CrawlRequest(BaseModel):
    """Request body for the POST /crawl endpoint.

    Allows the user to configure crawl parameters per-request,
    overriding system defaults.
    """

    url: HttpUrl = Field(description="Target URL to start crawling from")
    max_depth: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum navigation depth from the start URL",
    )
    max_pages: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of pages to crawl",
    )
    extract_elements: bool = Field(
        default=True,
        description="Whether to extract interactive DOM elements from each page",
    )
    screenshot_pages: bool = Field(
        default=True,
        description="Whether to capture a screenshot of each page",
    )
    generate_tests: bool = Field(
        default=True,
        description="Whether to auto-generate test scripts from the crawl results",
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )
    browser: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser engine to use for crawling",
    )


class CrawlPageSummary(BaseModel):
    """Summary of a single discovered page in the crawl response."""

    url: str = Field(description="Page URL")
    title: str = Field(default="", description="Page title")
    depth: int = Field(default=0, description="Navigation depth from start URL")
    elements_count: int = Field(default=0, description="Number of interactive elements found")
    links_count: int = Field(default=0, description="Number of outgoing links discovered")
    has_screenshot: bool = Field(default=False, description="Whether a screenshot was captured")


class CrawlTestGenSummary(BaseModel):
    """Summary of test generation from crawl results."""

    pom_files_generated: int = Field(default=0, description="POM class files created")
    test_files_generated: int = Field(default=0, description="Test script files created")
    total_files: int = Field(default=0, description="Total generated files")
    output_directory: str = Field(default="", description="Directory containing generated files")


class CrawlResponse(BaseModel):
    """Response body for the POST /crawl endpoint.

    Contains a summary of the crawl operation including discovered
    pages, element counts, suggested flows, and test generation status.
    """

    status: Literal["completed", "partial", "failed"] = Field(
        description="Overall crawl status"
    )
    start_url: str = Field(description="The URL crawling started from")
    total_pages: int = Field(default=0, description="Total pages discovered")
    max_depth_reached: int = Field(default=0, description="Maximum depth navigated")
    pages: list[CrawlPageSummary] = Field(
        default_factory=list,
        description="Summary of each discovered page",
    )
    suggested_flows: list[str] = Field(
        default_factory=list,
        description="Identified user flows from the site structure",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors encountered during crawling",
    )
    test_generation: CrawlTestGenSummary | None = Field(
        default=None,
        description="Test generation summary (if generate_tests=true)",
    )
    report_path: str = Field(
        default="",
        description="Path to the generated site map report",
    )
    duration_seconds: float = Field(
        default=0.0,
        description="Total crawl duration in seconds",
    )
