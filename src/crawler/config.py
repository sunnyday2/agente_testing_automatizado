"""Crawler configuration dataclass.

Defines all configurable parameters for the site discovery crawler,
including depth limits, timeouts, exclude patterns, and browser settings.

Usage:
    from src.crawler.config import CrawlConfig

    config = CrawlConfig(max_depth=3, max_pages=50)
    config = CrawlConfig.from_settings()  # Load from app settings
"""

import re
from dataclasses import dataclass, field
from typing import Literal

from src.config.settings import get_settings


# Default URL patterns to exclude from crawling
DEFAULT_EXCLUDE_PATTERNS = [
    r".*\.(pdf|zip|tar|gz|rar|7z)$",
    r".*\.(png|jpg|jpeg|gif|svg|ico|webp|bmp)$",
    r".*\.(mp3|mp4|avi|mov|wmv|flv)$",
    r".*\.(css|js|woff|woff2|ttf|eot)$",
    r".*logout.*",
    r".*sign.?out.*",
    r".*#.*",
    r".*mailto:.*",
    r".*tel:.*",
    r".*javascript:.*",
]


@dataclass
class CrawlConfig:
    """Configuration for the site crawler engine.

    Controls crawl behavior including depth limits, page limits,
    timeouts, browser settings, and URL filtering.

    Attributes:
        max_depth: Maximum navigation depth from the start URL.
        max_pages: Maximum number of pages to crawl.
        timeout_per_page: Timeout for each page load in milliseconds.
        exclude_patterns: Regex patterns for URLs to skip.
        extract_elements: Whether to extract interactive DOM elements.
        screenshot_pages: Whether to capture screenshots per page.
        headless: Run browser in headless mode.
        browser: Browser engine to use.
        viewport_width: Browser viewport width in pixels.
        viewport_height: Browser viewport height in pixels.
        wait_after_load: Milliseconds to wait after page load for dynamic content.
        respect_robots_txt: Whether to check and respect robots.txt rules.
        allowed_domains: If set, only crawl URLs on these domains.
        user_agent: Custom user agent string.
    """

    max_depth: int = 3
    max_pages: int = 50
    timeout_per_page: int = 10000
    exclude_patterns: list[str] = field(default_factory=lambda: DEFAULT_EXCLUDE_PATTERNS.copy())
    extract_elements: bool = True
    screenshot_pages: bool = True
    headless: bool = True
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    viewport_width: int = 1280
    viewport_height: int = 720
    wait_after_load: int = 1000
    respect_robots_txt: bool = True
    allowed_domains: list[str] = field(default_factory=list)
    user_agent: str = "QAAutomationAgent/1.0 (Playwright Crawler)"

    def __post_init__(self) -> None:
        """Compile exclude patterns into regex objects for efficient matching."""
        self._compiled_patterns: list[re.Pattern] = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.exclude_patterns
        ]

    def is_excluded(self, url: str) -> bool:
        """Check if a URL matches any exclude pattern.

        Args:
            url: The URL to check.

        Returns:
            True if the URL should be excluded from crawling.
        """
        return any(pattern.match(url) for pattern in self._compiled_patterns)

    def is_allowed_domain(self, url: str) -> bool:
        """Check if a URL belongs to an allowed domain.

        If allowed_domains is empty, all domains are allowed.

        Args:
            url: The URL to check.

        Returns:
            True if the URL's domain is allowed.
        """
        if not self.allowed_domains:
            return True

        from urllib.parse import urlparse

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        return any(
            domain == allowed.lower() or domain.endswith(f".{allowed.lower()}")
            for allowed in self.allowed_domains
        )

    @classmethod
    def from_settings(cls) -> "CrawlConfig":
        """Create a CrawlConfig from application settings.

        Returns:
            CrawlConfig populated from the current environment settings.
        """
        settings = get_settings()
        return cls(
            max_depth=settings.crawler.max_depth,
            max_pages=settings.crawler.max_pages,
            timeout_per_page=settings.crawler.timeout_per_page,
            extract_elements=settings.crawler.extract_elements,
            screenshot_pages=settings.crawler.screenshot_pages,
            headless=settings.crawler.headless,
            browser=settings.crawler.browser,
        )
