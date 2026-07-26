"""Site map construction and report generation.

Builds a structured SiteMap from crawled page data, generates summary
reports in Markdown format, and provides utilities for analyzing site
structure and navigation patterns.

Usage:
    from src.crawler.sitemap_builder import SiteMapBuilder

    builder = SiteMapBuilder()
    builder.add_page(page_node)
    site_map = builder.build(start_url="https://example.com")
    report = builder.generate_report()
"""

from datetime import datetime, timezone
from pathlib import Path

from src.agent.state import CrawlResults, PageNode, SiteMap
from src.common.logging import get_logger

logger = get_logger(__name__)


class SiteMapBuilder:
    """Builds and manages site map data from crawled pages.

    Aggregates PageNode objects from the crawler and provides
    methods to build the final SiteMap, generate reports, and
    analyze the site structure.
    """

    def __init__(self) -> None:
        """Initialize the site map builder."""
        self._pages: list[PageNode] = []
        self._start_url: str = ""

    def add_page(self, page: PageNode) -> None:
        """Add a discovered page to the site map.

        Args:
            page: A PageNode object from the crawler.
        """
        self._pages.append(page)

    def add_pages(self, pages: list[PageNode]) -> None:
        """Add multiple pages at once.

        Args:
            pages: List of PageNode objects.
        """
        self._pages.extend(pages)

    def build(self, start_url: str) -> SiteMap:
        """Build the final SiteMap object.

        Args:
            start_url: The URL crawling started from.

        Returns:
            Complete SiteMap with all discovered pages and metadata.
        """
        self._start_url = start_url

        site_map = SiteMap(
            start_url=start_url,
            pages=self._pages,
            total_pages=len(self._pages),
            max_depth_reached=max((p.depth for p in self._pages), default=0),
        )

        logger.info(
            "sitemap_built",
            start_url=start_url,
            total_pages=site_map.total_pages,
            max_depth=site_map.max_depth_reached,
        )

        return site_map

    def generate_report(self, output_path: str | None = None) -> str:
        """Generate a Markdown summary report of the site map.

        Includes page inventory, element counts, navigation structure,
        and suggested test areas.

        Args:
            output_path: Optional file path to write the report.
                If provided, saves the report to disk.

        Returns:
            The complete Markdown report as a string.
        """
        report_lines: list[str] = []

        # Header
        report_lines.append("# Site Map Report")
        report_lines.append("")
        report_lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}")
        report_lines.append(f"**Start URL:** {self._start_url}")
        report_lines.append(f"**Total Pages:** {len(self._pages)}")
        max_depth = max((p.depth for p in self._pages), default=0)
        report_lines.append(f"**Max Depth Reached:** {max_depth}")
        report_lines.append("")

        # Summary statistics
        report_lines.append("## Summary Statistics")
        report_lines.append("")
        total_elements = sum(len(p.elements) for p in self._pages)
        total_links = sum(len(p.links) for p in self._pages)
        pages_with_forms = sum(
            1 for p in self._pages
            if any(e.tag == "input" or e.tag == "textarea" or e.tag == "select" for e in p.elements)
        )
        pages_with_buttons = sum(
            1 for p in self._pages if any(e.tag == "button" for e in p.elements)
        )
        report_lines.append(f"| Metric | Value |")
        report_lines.append(f"|--------|-------|")
        report_lines.append(f"| Total interactive elements | {total_elements} |")
        report_lines.append(f"| Total outgoing links | {total_links} |")
        report_lines.append(f"| Pages with forms | {pages_with_forms} |")
        report_lines.append(f"| Pages with action buttons | {pages_with_buttons} |")
        report_lines.append("")

        # Pages by depth
        report_lines.append("## Pages by Depth")
        report_lines.append("")
        depth_groups: dict[int, list[PageNode]] = {}
        for page in self._pages:
            depth_groups.setdefault(page.depth, []).append(page)

        for depth in sorted(depth_groups.keys()):
            pages_at_depth = depth_groups[depth]
            report_lines.append(f"### Depth {depth} ({len(pages_at_depth)} pages)")
            report_lines.append("")
            for page in pages_at_depth:
                element_count = len(page.elements)
                report_lines.append(
                    f"- **{page.title or 'Untitled'}** — `{page.url}` "
                    f"({element_count} elements, {len(page.links)} links)"
                )
            report_lines.append("")

        # Page details
        report_lines.append("## Page Details")
        report_lines.append("")

        for i, page in enumerate(self._pages, 1):
            report_lines.append(f"### {i}. {page.title or 'Untitled'}")
            report_lines.append(f"- **URL:** {page.url}")
            report_lines.append(f"- **Depth:** {page.depth}")
            report_lines.append(f"- **Elements:** {len(page.elements)}")

            if page.screenshot_path:
                report_lines.append(f"- **Screenshot:** `{page.screenshot_path}`")

            if page.elements:
                report_lines.append("")
                report_lines.append("| Tag | Type | Text | Selector |")
                report_lines.append("|-----|------|------|----------|")
                for elem in page.elements[:15]:  # Limit table size
                    text_preview = elem.text[:30] if elem.text else "-"
                    report_lines.append(
                        f"| {elem.tag} | {elem.element_type or '-'} | "
                        f"{text_preview} | `{elem.selector}` |"
                    )
                if len(page.elements) > 15:
                    report_lines.append(
                        f"| ... | ... | *{len(page.elements) - 15} more elements* | ... |"
                    )

            report_lines.append("")

        # Test coverage suggestions
        report_lines.append("## Suggested Test Areas")
        report_lines.append("")
        suggestions = self._generate_test_suggestions()
        for i, suggestion in enumerate(suggestions, 1):
            report_lines.append(f"{i}. {suggestion}")
        report_lines.append("")

        report = "\n".join(report_lines)

        # Write to file if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(report, encoding="utf-8")
            logger.info("sitemap_report_saved", path=output_path)

        return report

    def _generate_test_suggestions(self) -> list[str]:
        """Generate test area suggestions based on the site structure.

        Returns:
            List of suggested test areas.
        """
        suggestions: list[str] = []

        # Forms
        form_pages = [
            p for p in self._pages
            if any(e.tag in ("input", "textarea", "select") for e in p.elements)
        ]
        if form_pages:
            suggestions.append(
                f"Form validation tests for {len(form_pages)} page(s) with input fields"
            )

        # Authentication
        auth_pages = [
            p for p in self._pages
            if any(
                kw in p.url.lower() or kw in p.title.lower()
                for kw in ["login", "signin", "register", "signup", "auth"]
            )
        ]
        if auth_pages:
            suggestions.append(
                f"Authentication flow tests: {', '.join(p.title or p.url for p in auth_pages)}"
            )

        # Navigation
        if len(self._pages) > 3:
            suggestions.append(
                f"Navigation flow tests across {len(self._pages)} discovered pages"
            )

        # Buttons/Actions
        action_pages = [
            p for p in self._pages
            if any(e.tag == "button" for e in p.elements)
        ]
        if action_pages:
            total_buttons = sum(
                sum(1 for e in p.elements if e.tag == "button") for p in action_pages
            )
            suggestions.append(
                f"Button interaction tests: {total_buttons} buttons across {len(action_pages)} pages"
            )

        # Deep pages (might indicate complex flows)
        deep_pages = [p for p in self._pages if p.depth >= 2]
        if deep_pages:
            suggestions.append(
                f"Deep navigation tests for {len(deep_pages)} page(s) at depth >= 2"
            )

        # External links (potential broken link tests)
        pages_with_many_links = [p for p in self._pages if len(p.links) > 10]
        if pages_with_many_links:
            suggestions.append(
                f"Link integrity tests for {len(pages_with_many_links)} page(s) with 10+ outgoing links"
            )

        if not suggestions:
            suggestions.append("Basic page load and rendering tests for all discovered pages")

        return suggestions

    def get_navigation_tree(self) -> dict:
        """Build a tree structure representing page navigation hierarchy.

        Returns:
            Dictionary representing the navigation tree.
        """
        tree: dict = {"url": self._start_url, "children": {}}

        # Sort pages by depth
        sorted_pages = sorted(self._pages, key=lambda p: p.depth)

        url_to_node: dict[str, dict] = {self._start_url: tree}

        for page in sorted_pages:
            page_node = {
                "url": page.url,
                "title": page.title,
                "depth": page.depth,
                "elements_count": len(page.elements),
                "children": {},
            }
            url_to_node[page.url] = page_node

            # Try to find parent (page that links to this one)
            parent_found = False
            for potential_parent in sorted_pages:
                if potential_parent.depth == page.depth - 1 and page.url in potential_parent.links:
                    parent_key = potential_parent.url
                    if parent_key in url_to_node:
                        url_to_node[parent_key]["children"][page.url] = page_node
                        parent_found = True
                        break

            # If no parent found, attach to root
            if not parent_found and page.url != self._start_url:
                tree["children"][page.url] = page_node

        return tree
