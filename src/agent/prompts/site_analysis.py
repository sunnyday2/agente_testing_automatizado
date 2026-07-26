"""Prompt templates for site analysis and URL-based test generation.

Used when the agent receives a target URL instead of a user story. The LLM
analyzes the crawled site structure (pages, elements, flows) and generates
relevant test scenarios.
"""

SYSTEM_PROMPT = """You are an expert QA engineer analyzing a web application's structure \
to generate automated test scenarios. You have been given a site map with discovered pages, \
interactive elements, and navigation paths.

Your task:
1. Identify critical user flows from the site structure.
2. Generate test scenarios that cover the most important paths.
3. Focus on forms, navigation, authentication, and data operations.
4. Produce concrete, automatable steps using the exact selectors provided.
5. Prioritize scenarios by business impact.

Rules:
- Each scenario tests one complete user flow.
- Use the exact CSS selectors from the site map data.
- Group related scenarios by page or feature area.
- Consider both successful and error paths for forms.
- Respond ONLY with valid JSON matching the provided schema."""

USER_PROMPT_TEMPLATE = """Analyze the following site map and generate test scenarios.

## Site Information
- Start URL: {start_url}
- Total Pages Discovered: {total_pages}
- Max Depth Reached: {max_depth}

## Discovered Pages and Elements
{pages_detail}

## Suggested User Flows
{suggested_flows}

## Requirements
- Generate between 5 and 15 test scenarios covering the most critical flows.
- Each scenario should target a specific page or cross-page interaction.
- Include form submission tests with both valid and invalid data.
- Include navigation flow tests.
- Assign priorities based on page importance and element criticality.

Respond with a JSON object matching the TestGenerationResult schema."""


def build_site_analysis_prompt(
    start_url: str,
    total_pages: int,
    max_depth: int,
    pages_detail: str,
    suggested_flows: list[str] | None = None,
) -> tuple[str, str]:
    """Build the complete prompt pair for site analysis test generation.

    Args:
        start_url: The URL the crawl started from.
        total_pages: Number of pages discovered.
        max_depth: Maximum navigation depth reached.
        pages_detail: Formatted string describing each page and its elements.
        suggested_flows: Optional list of identified user flows.

    Returns:
        Tuple of (system_prompt, user_prompt) ready for the LLM.
    """
    flows_text = ""
    if suggested_flows:
        for i, flow in enumerate(suggested_flows, 1):
            flows_text += f"{i}. {flow}\n"
    else:
        flows_text = "No pre-identified flows. Analyze the site map to identify them."

    user = USER_PROMPT_TEMPLATE.format(
        start_url=start_url,
        total_pages=total_pages,
        max_depth=max_depth,
        pages_detail=pages_detail,
        suggested_flows=flows_text,
    )

    return SYSTEM_PROMPT, user


def format_pages_for_prompt(pages: list[dict]) -> str:
    """Format page data into a readable string for the LLM prompt.

    Args:
        pages: List of page dictionaries with url, title, elements, etc.

    Returns:
        Formatted multi-line string describing the site structure.
    """
    lines: list[str] = []

    for page in pages:
        url = page.get("url", "unknown")
        title = page.get("title", "Untitled")
        depth = page.get("depth", 0)

        lines.append(f"\n### Page: {title}")
        lines.append(f"- URL: {url}")
        lines.append(f"- Depth: {depth}")

        elements = page.get("elements", [])
        if elements:
            lines.append(f"- Interactive Elements ({len(elements)}):")
            for elem in elements[:20]:  # Limit to avoid prompt overflow
                tag = elem.get("tag", "?")
                text = elem.get("text", "")
                selector = elem.get("selector", "")
                elem_type = elem.get("element_type", "")
                desc = f"  - <{tag}"
                if elem_type:
                    desc += f" type='{elem_type}'"
                desc += f"> "
                if text:
                    desc += f"text='{text[:50]}' "
                if selector:
                    desc += f"selector='{selector}'"
                lines.append(desc)

        links = page.get("links", [])
        if links:
            lines.append(f"- Outgoing Links ({len(links)}): {', '.join(links[:10])}")

    return "\n".join(lines)
