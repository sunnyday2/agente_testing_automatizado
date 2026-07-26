"""DOM element cataloging for crawled pages.

Provides a dedicated service for extracting and cataloging interactive
elements from a web page. Used by the crawler engine to build a complete
inventory of actionable elements per page for test generation.

Usage:
    from src.crawler.element_extractor import ElementExtractor

    extractor = ElementExtractor()
    elements = await extractor.extract(page)
    summary = extractor.summarize(elements)
"""

from dataclasses import dataclass, field
from typing import Literal

from playwright.async_api import Page

from src.agent.state import PageElement
from src.common.logging import get_logger

logger = get_logger(__name__)

# Element categories and their CSS selectors
ELEMENT_CATEGORIES: dict[str, str] = {
    "button": "button, input[type='button'], input[type='submit'], input[type='reset'], [role='button']",
    "input": "input:not([type='hidden']):not([type='button']):not([type='submit']):not([type='reset'])",
    "link": "a[href]:not([href^='#']):not([href^='javascript:'])",
    "select": "select",
    "textarea": "textarea",
    "checkbox": "input[type='checkbox']",
    "radio": "input[type='radio']",
    "file_input": "input[type='file']",
}

# Maximum elements to extract per category to avoid overwhelming the LLM
MAX_ELEMENTS_PER_CATEGORY = 30


@dataclass
class ElementCatalog:
    """Structured catalog of all interactive elements on a page.

    Provides aggregated views and filtering capabilities for
    downstream test generation.

    Attributes:
        elements: All extracted PageElement objects.
        page_url: The source page URL.
        page_title: The page title.
        by_category: Elements grouped by category.
    """

    elements: list[PageElement] = field(default_factory=list)
    page_url: str = ""
    page_title: str = ""
    by_category: dict[str, list[PageElement]] = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        """Total number of cataloged elements."""
        return len(self.elements)

    @property
    def has_forms(self) -> bool:
        """Whether the page has form-related elements."""
        form_categories = {"input", "select", "textarea", "checkbox", "radio", "file_input"}
        return any(cat in self.by_category and self.by_category[cat] for cat in form_categories)

    @property
    def has_navigation(self) -> bool:
        """Whether the page has navigation links."""
        return bool(self.by_category.get("link"))

    @property
    def has_actions(self) -> bool:
        """Whether the page has clickable action elements."""
        return bool(self.by_category.get("button"))

    def get_form_elements(self) -> list[PageElement]:
        """Return all form-related elements (inputs, selects, textareas)."""
        form_elements: list[PageElement] = []
        for cat in ("input", "select", "textarea", "checkbox", "radio", "file_input"):
            form_elements.extend(self.by_category.get(cat, []))
        return form_elements

    def get_action_elements(self) -> list[PageElement]:
        """Return all action elements (buttons)."""
        return self.by_category.get("button", [])

    def get_navigation_elements(self) -> list[PageElement]:
        """Return all navigation elements (links)."""
        return self.by_category.get("link", [])


class ElementExtractor:
    """Extracts and catalogs interactive DOM elements from a web page.

    Identifies buttons, inputs, links, selects, textareas, checkboxes,
    radio buttons, and file inputs. Builds selectors prioritizing stable
    attributes (id, data-testid, name, aria-label).
    """

    def __init__(self, max_per_category: int = MAX_ELEMENTS_PER_CATEGORY) -> None:
        """Initialize the element extractor.

        Args:
            max_per_category: Maximum elements to extract per category.
        """
        self._max_per_category = max_per_category

    async def extract(self, page: Page) -> ElementCatalog:
        """Extract all interactive elements from the page.

        Args:
            page: A Playwright Page object (already navigated).

        Returns:
            ElementCatalog with all discovered elements grouped by category.
        """
        page_url = page.url
        page_title = await page.title()

        catalog = ElementCatalog(
            page_url=page_url,
            page_title=page_title,
        )

        for category, selector in ELEMENT_CATEGORIES.items():
            try:
                elements = await self._extract_category(page, category, selector)
                if elements:
                    catalog.by_category[category] = elements
                    catalog.elements.extend(elements)
            except Exception as e:
                logger.warning(
                    "element_category_extraction_failed",
                    category=category,
                    url=page_url,
                    error=str(e),
                )

        logger.info(
            "elements_extracted",
            url=page_url,
            total=catalog.total_count,
            categories=len(catalog.by_category),
            has_forms=catalog.has_forms,
            has_actions=catalog.has_actions,
        )

        return catalog

    async def _extract_category(
        self,
        page: Page,
        category: str,
        selector: str,
    ) -> list[PageElement]:
        """Extract elements for a single category.

        Args:
            page: The Playwright page.
            category: Category name (e.g., "button", "input").
            selector: CSS selector to find elements.

        Returns:
            List of extracted PageElement objects.
        """
        elements: list[PageElement] = []
        locators = page.locator(selector)
        count = await locators.count()

        for i in range(min(count, self._max_per_category)):
            locator = locators.nth(i)

            try:
                # Skip hidden elements
                if not await locator.is_visible():
                    continue

                element = await self._extract_single(locator, category)
                if element:
                    elements.append(element)

            except Exception:
                # Skip individual elements that fail
                continue

        return elements

    async def _extract_single(
        self,
        locator,
        category: str,
    ) -> PageElement | None:
        """Extract data from a single DOM element.

        Args:
            locator: Playwright Locator pointing to the element.
            category: The element category.

        Returns:
            PageElement if extraction succeeds, None otherwise.
        """
        try:
            tag_name = await locator.evaluate("el => el.tagName.toLowerCase()")
            elem_type = await locator.get_attribute("type") or ""
            aria_label = await locator.get_attribute("aria-label") or ""

            # Get text content (truncated)
            text = ""
            try:
                raw_text = await locator.text_content()
                if raw_text:
                    text = raw_text.strip()[:100]
            except Exception:
                pass

            # For inputs, use placeholder as text hint if no label
            if not text and category in ("input", "textarea"):
                placeholder = await locator.get_attribute("placeholder") or ""
                text = placeholder[:100]

            # Build a stable CSS selector
            css_selector = await self._build_stable_selector(locator, tag_name, elem_type)

            return PageElement(
                tag=tag_name,
                element_type=elem_type,
                text=text,
                selector=css_selector,
                aria_label=aria_label,
            )

        except Exception:
            return None

    async def _build_stable_selector(
        self,
        locator,
        tag_name: str,
        elem_type: str,
    ) -> str:
        """Build the most stable CSS selector for an element.

        Priority order:
        1. #id (most stable)
        2. [data-testid='...'] (test-specific)
        3. [name='...'] (form elements)
        4. [aria-label='...'] (accessible elements)
        5. tag[type='...'] (type-based)
        6. tag (fallback)

        Args:
            locator: Playwright locator for the element.
            tag_name: HTML tag name.
            elem_type: Element type attribute.

        Returns:
            Best available CSS selector string.
        """
        # Try ID
        elem_id = await locator.get_attribute("id")
        if elem_id and not elem_id.startswith(":"):  # Skip auto-generated IDs
            return f"#{elem_id}"

        # Try data-testid
        testid = await locator.get_attribute("data-testid")
        if testid:
            return f"[data-testid='{testid}']"

        # Try data-cy (Cypress convention)
        data_cy = await locator.get_attribute("data-cy")
        if data_cy:
            return f"[data-cy='{data_cy}']"

        # Try name attribute
        name = await locator.get_attribute("name")
        if name:
            return f"{tag_name}[name='{name}']"

        # Try aria-label
        aria = await locator.get_attribute("aria-label")
        if aria:
            return f"{tag_name}[aria-label='{aria}']"

        # Try type for inputs
        if elem_type and tag_name == "input":
            return f"input[type='{elem_type}']"

        # Fallback to tag name
        return tag_name

    def summarize(self, catalog: ElementCatalog) -> str:
        """Generate a human-readable summary of the element catalog.

        Args:
            catalog: The ElementCatalog to summarize.

        Returns:
            Multi-line summary string.
        """
        lines: list[str] = [
            f"Page: {catalog.page_title} ({catalog.page_url})",
            f"Total elements: {catalog.total_count}",
            "",
            "Categories:",
        ]

        for category, elements in catalog.by_category.items():
            lines.append(f"  {category}: {len(elements)} elements")
            # Show first 3 examples
            for elem in elements[:3]:
                desc = f"    - <{elem.tag}"
                if elem.element_type:
                    desc += f" type='{elem.element_type}'"
                desc += f"> "
                if elem.text:
                    desc += f"'{elem.text[:40]}' "
                desc += f"[{elem.selector}]"
                lines.append(desc)
            if len(elements) > 3:
                lines.append(f"    ... and {len(elements) - 3} more")

        lines.append("")
        lines.append("Capabilities:")
        lines.append(f"  Has forms: {catalog.has_forms}")
        lines.append(f"  Has actions: {catalog.has_actions}")
        lines.append(f"  Has navigation: {catalog.has_navigation}")

        return "\n".join(lines)
