"""Playwright-based BFS site crawler engine.

Navigates a target site using breadth-first search, discovering pages,
extracting interactive elements, and building a site map. Respects
depth limits, page limits, robots.txt, and exclude patterns.

Usage:
    from src.crawler.engine import CrawlerEngine
    from src.crawler.config import CrawlConfig

    config = CrawlConfig(max_depth=3, max_pages=50)
    engine = CrawlerEngine(config)
    result = await engine.crawl("https://example.com")
"""

import re
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from src.agent.state import CrawlResults, PageElement, PageNode, SiteMap
from src.common.exceptions import CrawlerError, NavigationError
from src.common.logging import get_logger
from src.crawler.config import CrawlConfig

logger = get_logger(__name__)


class CrawlerEngine:
    """BFS site crawler using Playwright for real browser rendering.

    Discovers pages by following links in breadth-first order, respecting
    configured limits and filtering rules. Extracts interactive elements
    from each page for test generation.
    """

    def __init__(self, config: CrawlConfig | None = None) -> None:
        """Initialize the crawler engine.

        Args:
            config: Crawler configuration. Defaults to settings-based config.
        """
        self._config = config or CrawlConfig.from_settings()
        self._visited: set[str] = set()
        self._robots_parser: RobotFileParser | None = None
        self._base_domain: str = ""

    async def crawl(self, start_url: str, screenshot_dir: str | None = None) -> CrawlResults:
        """Crawl a site starting from the given URL.

        Performs BFS traversal, extracting page data and building
        a complete site map.

        Args:
            start_url: The URL to begin crawling from.
            screenshot_dir: Directory to save screenshots. Defaults to
                data/allure-results/screenshots/.

        Returns:
            CrawlResults with the discovered site map and suggested flows.

        Raises:
            CrawlerError: If the crawler cannot start (invalid URL, etc).
        """
        # Reset state for a new crawl
        self._visited.clear()
        self._base_domain = urlparse(start_url).netloc

        # Set up screenshot directory
        if screenshot_dir is None:
            screenshot_dir = str(
                Path(__file__).resolve().parent.parent.parent
                / "data"
                / "allure-results"
                / "screenshots"
            )
        Path(screenshot_dir).mkdir(parents=True, exist_ok=True)

        # Load robots.txt if configured
        if self._config.respect_robots_txt:
            await self._load_robots_txt(start_url)

        logger.info(
            "crawl_started",
            start_url=start_url,
            max_depth=self._config.max_depth,
            max_pages=self._config.max_pages,
        )

        pages: list[PageNode] = []
        errors: list[str] = []

        async with async_playwright() as p:
            browser = await self._launch_browser(p)
            context = await self._create_context(browser)

            try:
                pages, errors = await self._bfs_crawl(
                    context, start_url, screenshot_dir
                )
            finally:
                await context.close()
                await browser.close()

        # Build site map
        site_map = SiteMap(
            start_url=start_url,
            pages=pages,
            total_pages=len(pages),
            max_depth_reached=max((p.depth for p in pages), default=0),
        )

        # Identify suggested user flows
        suggested_flows = self._identify_flows(pages)

        result = CrawlResults(
            site_map=site_map,
            suggested_flows=suggested_flows,
            errors=errors,
        )

        logger.info(
            "crawl_completed",
            total_pages=len(pages),
            total_errors=len(errors),
            max_depth=site_map.max_depth_reached,
            suggested_flows=len(suggested_flows),
        )

        return result

    async def _bfs_crawl(
        self,
        context: BrowserContext,
        start_url: str,
        screenshot_dir: str,
    ) -> tuple[list[PageNode], list[str]]:
        """Perform BFS traversal of the site.

        Args:
            context: Playwright browser context.
            start_url: Starting URL.
            screenshot_dir: Directory for screenshots.

        Returns:
            Tuple of (discovered pages, error messages).
        """
        pages: list[PageNode] = []
        errors: list[str] = []

        # BFS queue: (url, depth)
        queue: deque[tuple[str, int]] = deque()
        queue.append((self._normalize_url(start_url), 0))

        while queue and len(pages) < self._config.max_pages:
            url, depth = queue.popleft()

            # Skip if already visited
            normalized = self._normalize_url(url)
            if normalized in self._visited:
                continue

            # Skip if exceeds max depth
            if depth > self._config.max_depth:
                continue

            # Skip if excluded by patterns
            if self._config.is_excluded(url):
                continue

            # Skip if not on allowed domain
            if not self._config.is_allowed_domain(url):
                continue

            # Skip if blocked by robots.txt
            if not self._is_allowed_by_robots(url):
                continue

            # Mark as visited
            self._visited.add(normalized)

            # Process the page
            try:
                page_node = await self._process_page(
                    context, url, depth, screenshot_dir
                )
                pages.append(page_node)

                # Add discovered links to the queue
                for link in page_node.links:
                    link_normalized = self._normalize_url(link)
                    if link_normalized not in self._visited:
                        queue.append((link, depth + 1))

            except NavigationError as e:
                error_msg = f"[depth={depth}] {e.message}"
                errors.append(error_msg)
                logger.warning("page_crawl_failed", url=url, error=str(e))
            except Exception as e:
                error_msg = f"[depth={depth}] Unexpected error on {url}: {e}"
                errors.append(error_msg)
                logger.error("page_crawl_unexpected_error", url=url, error=str(e))

        return pages, errors

    async def _process_page(
        self,
        context: BrowserContext,
        url: str,
        depth: int,
        screenshot_dir: str,
    ) -> PageNode:
        """Process a single page: navigate, extract elements, capture screenshot.

        Args:
            context: Browser context.
            url: URL to navigate to.
            depth: Current crawl depth.
            screenshot_dir: Directory for screenshots.

        Returns:
            PageNode with extracted page data.

        Raises:
            NavigationError: If the page cannot be loaded.
        """
        page = await context.new_page()

        try:
            # Navigate to the page
            response = await page.goto(
                url,
                timeout=self._config.timeout_per_page,
                wait_until="domcontentloaded",
            )

            if response is None or response.status >= 400:
                status = response.status if response else 0
                raise NavigationError(
                    url=url,
                    reason=f"HTTP {status}",
                )

            # Wait for dynamic content
            await page.wait_for_timeout(self._config.wait_after_load)

            # Get page title
            title = await page.title()

            # Extract interactive elements
            elements: list[PageElement] = []
            if self._config.extract_elements:
                elements = await self._extract_elements(page)

            # Discover links on the page
            links = await self._extract_links(page, url)

            # Capture screenshot
            screenshot_path = ""
            if self._config.screenshot_pages:
                screenshot_path = await self._capture_screenshot(
                    page, url, screenshot_dir
                )

            return PageNode(
                url=url,
                title=title,
                depth=depth,
                elements=elements,
                links=links,
                screenshot_path=screenshot_path,
            )

        except NavigationError:
            raise
        except Exception as e:
            raise NavigationError(url=url, reason=str(e)) from e
        finally:
            await page.close()

    async def _extract_elements(self, page: Page) -> list[PageElement]:
        """Extract interactive DOM elements from the page.

        Identifies buttons, links, inputs, selects, and textareas.

        Args:
            page: The Playwright page object.

        Returns:
            List of PageElement objects representing interactive elements.
        """
        elements: list[PageElement] = []

        # Selectors for interactive elements
        selectors = [
            ("button", "button, input[type='button'], input[type='submit']"),
            ("input", "input:not([type='hidden'])"),
            ("link", "a[href]"),
            ("select", "select"),
            ("textarea", "textarea"),
        ]

        for tag_category, selector in selectors:
            try:
                locators = page.locator(selector)
                count = await locators.count()

                for i in range(min(count, 50)):  # Limit per category
                    locator = locators.nth(i)

                    try:
                        # Check visibility
                        if not await locator.is_visible():
                            continue

                        tag_name = await locator.evaluate("el => el.tagName.toLowerCase()")
                        elem_type = await locator.get_attribute("type") or ""
                        text = (await locator.text_content() or "").strip()[:100]
                        aria_label = await locator.get_attribute("aria-label") or ""

                        # Build a reliable selector
                        css_selector = await self._build_selector(locator, page)

                        elements.append(
                            PageElement(
                                tag=tag_name,
                                element_type=elem_type,
                                text=text,
                                selector=css_selector,
                                aria_label=aria_label,
                            )
                        )
                    except Exception:
                        # Skip individual elements that fail extraction
                        continue

            except Exception:
                # Skip entire category on failure
                continue

        return elements

    async def _build_selector(self, locator, page: Page) -> str:
        """Build a CSS selector for an element.

        Tries id, name, data-testid, then falls back to a generated selector.

        Args:
            locator: Playwright locator for the element.
            page: The page object.

        Returns:
            A CSS selector string.
        """
        try:
            # Try common unique attributes
            elem_id = await locator.get_attribute("id")
            if elem_id:
                return f"#{elem_id}"

            data_testid = await locator.get_attribute("data-testid")
            if data_testid:
                return f"[data-testid='{data_testid}']"

            name = await locator.get_attribute("name")
            if name:
                tag = await locator.evaluate("el => el.tagName.toLowerCase()")
                return f"{tag}[name='{name}']"

            # Fallback: use aria-label or text content
            aria = await locator.get_attribute("aria-label")
            if aria:
                tag = await locator.evaluate("el => el.tagName.toLowerCase()")
                return f"{tag}[aria-label='{aria}']"

            # Last resort: tag + type + nth
            tag = await locator.evaluate("el => el.tagName.toLowerCase()")
            elem_type = await locator.get_attribute("type")
            if elem_type:
                return f"{tag}[type='{elem_type}']"

            return tag

        except Exception:
            return "unknown"

    async def _extract_links(self, page: Page, current_url: str) -> list[str]:
        """Extract and filter navigation links from the page.

        Only returns links that are on the same domain and not excluded.

        Args:
            page: The Playwright page object.
            current_url: The current page URL for resolving relative links.

        Returns:
            List of absolute URLs discovered on the page.
        """
        links: list[str] = []

        try:
            hrefs = await page.eval_on_selector_all(
                "a[href]",
                "elements => elements.map(el => el.getAttribute('href'))",
            )

            for href in hrefs:
                if not href or href.startswith("#"):
                    continue

                # Resolve relative URLs
                absolute_url = urljoin(current_url, href)

                # Normalize
                normalized = self._normalize_url(absolute_url)

                # Filter: same domain, not excluded, not visited
                parsed = urlparse(normalized)
                if parsed.netloc != self._base_domain:
                    continue
                if self._config.is_excluded(normalized):
                    continue
                if normalized not in self._visited and normalized not in links:
                    links.append(normalized)

        except Exception as e:
            logger.warning("link_extraction_failed", url=current_url, error=str(e))

        return links

    async def _capture_screenshot(
        self, page: Page, url: str, screenshot_dir: str
    ) -> str:
        """Capture a full-page screenshot.

        Args:
            page: The Playwright page object.
            url: The page URL (used for filename).
            screenshot_dir: Directory to save the screenshot.

        Returns:
            Path to the saved screenshot file.
        """
        try:
            # Generate safe filename from URL
            parsed = urlparse(url)
            safe_name = re.sub(r"[^\w\-.]", "_", f"{parsed.netloc}{parsed.path}")
            safe_name = safe_name[:100]  # Limit filename length
            filename = f"{safe_name}.png"
            filepath = str(Path(screenshot_dir) / filename)

            await page.screenshot(path=filepath, full_page=True)
            return filepath

        except Exception as e:
            logger.warning("screenshot_failed", url=url, error=str(e))
            return ""

    def _normalize_url(self, url: str) -> str:
        """Normalize a URL for deduplication.

        Removes fragments, trailing slashes, and normalizes scheme/host.

        Args:
            url: The URL to normalize.

        Returns:
            Normalized URL string.
        """
        parsed = urlparse(url)

        # Remove fragment
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/") or "/",
            parsed.params,
            parsed.query,
            "",  # Remove fragment
        ))

        return normalized

    async def _load_robots_txt(self, start_url: str) -> None:
        """Load and parse robots.txt from the target site.

        Args:
            start_url: The start URL to derive robots.txt location.
        """
        try:
            parsed = urlparse(start_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            self._robots_parser = RobotFileParser()
            self._robots_parser.set_url(robots_url)
            self._robots_parser.read()

            logger.info("robots_txt_loaded", url=robots_url)

        except Exception as e:
            logger.warning("robots_txt_load_failed", error=str(e))
            self._robots_parser = None

    def _is_allowed_by_robots(self, url: str) -> bool:
        """Check if a URL is allowed by robots.txt rules.

        Args:
            url: The URL to check.

        Returns:
            True if the URL is allowed (or robots.txt is not available).
        """
        if not self._config.respect_robots_txt or self._robots_parser is None:
            return True

        try:
            return self._robots_parser.can_fetch(self._config.user_agent, url)
        except Exception:
            return True  # Allow on parser error

    async def _launch_browser(self, playwright) -> Browser:
        """Launch the configured browser.

        Args:
            playwright: The Playwright instance.

        Returns:
            A Browser instance.
        """
        browser_type = getattr(playwright, self._config.browser)
        return await browser_type.launch(headless=self._config.headless)

    async def _create_context(self, browser: Browser) -> BrowserContext:
        """Create a browser context with configured viewport and user agent.

        Args:
            browser: The browser instance.

        Returns:
            A BrowserContext instance.
        """
        return await browser.new_context(
            viewport={
                "width": self._config.viewport_width,
                "height": self._config.viewport_height,
            },
            user_agent=self._config.user_agent,
        )

    def _identify_flows(self, pages: list[PageNode]) -> list[str]:
        """Identify suggested user flows from discovered page structure.

        Analyzes page elements and navigation patterns to suggest
        meaningful test flows.

        Args:
            pages: List of discovered PageNode objects.

        Returns:
            List of suggested user flow descriptions.
        """
        flows: list[str] = []

        # Detect login flow
        login_pages = [
            p for p in pages
            if any(
                kw in p.url.lower() or kw in p.title.lower()
                for kw in ["login", "signin", "sign-in", "auth"]
            )
        ]
        if login_pages:
            flows.append("Authentication flow: login page → dashboard")

        # Detect forms
        pages_with_forms = [
            p for p in pages
            if any(e.tag == "input" and e.element_type not in ("hidden", "submit") for e in p.elements)
        ]
        if pages_with_forms:
            flows.append(
                f"Form submission flows across {len(pages_with_forms)} pages with input fields"
            )

        # Detect navigation patterns
        pages_with_nav = [
            p for p in pages
            if any(e.tag == "a" or (e.tag == "button" and "nav" in e.selector.lower()) for e in p.elements)
        ]
        if len(pages_with_nav) > 2:
            flows.append(
                f"Navigation flow: multi-page journey across {len(pages_with_nav)} interconnected pages"
            )

        # Detect CRUD patterns
        crud_keywords = ["create", "edit", "delete", "new", "update", "add", "remove"]
        crud_pages = [
            p for p in pages
            if any(kw in p.url.lower() or kw in p.title.lower() for kw in crud_keywords)
        ]
        if crud_pages:
            flows.append(f"CRUD operations: {len(crud_pages)} pages with data management")

        # Detect dashboard
        dashboard_pages = [
            p for p in pages
            if any(kw in p.url.lower() or kw in p.title.lower() for kw in ["dashboard", "home", "overview"])
        ]
        if dashboard_pages:
            flows.append("Dashboard overview: verify widget rendering and data display")

        if not flows:
            flows.append(f"General navigation: verify {len(pages)} discovered pages load correctly")

        return flows
