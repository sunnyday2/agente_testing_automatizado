"""Crawl endpoint for triggering site discovery.

Receives a target URL and crawl configuration, triggers the Playwright
BFS crawler, and optionally generates test scripts from the results.

Endpoint:
    POST /crawl
"""

import time

from fastapi import APIRouter

from src.api.schemas.crawl import (
    CrawlPageSummary,
    CrawlRequest,
    CrawlResponse,
    CrawlTestGenSummary,
)
from src.common.logging import get_logger
from src.crawler.config import CrawlConfig
from src.crawler.engine import CrawlerEngine
from src.crawler.sitemap_builder import SiteMapBuilder
from src.crawler.test_generator import CrawlTestGenerator

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/crawl",
    response_model=CrawlResponse,
    status_code=200,
)
async def trigger_crawl(request: CrawlRequest) -> CrawlResponse:
    """Trigger a site discovery crawl from the given URL.

    Navigates the target site using Playwright BFS, extracts elements,
    builds a site map, and optionally generates test scripts.

    Args:
        request: Crawl configuration with target URL and parameters.

    Returns:
        CrawlResponse with discovered pages, flows, and generation summary.
    """
    start_time = time.time()
    start_url = str(request.url)

    logger.info(
        "crawl_endpoint_triggered",
        url=start_url,
        max_depth=request.max_depth,
        max_pages=request.max_pages,
        generate_tests=request.generate_tests,
    )

    # Build crawler config from request
    config = CrawlConfig(
        max_depth=request.max_depth,
        max_pages=request.max_pages,
        extract_elements=request.extract_elements,
        screenshot_pages=request.screenshot_pages,
        headless=request.headless,
        browser=request.browser,
    )

    # Run the crawler
    engine = CrawlerEngine(config)

    try:
        crawl_results = await engine.crawl(start_url)
    except Exception as e:
        logger.error("crawl_failed", url=start_url, error=str(e))
        duration = time.time() - start_time
        return CrawlResponse(
            status="failed",
            start_url=start_url,
            errors=[str(e)],
            duration_seconds=round(duration, 2),
        )

    site_map = crawl_results.site_map

    # Generate site map report
    builder = SiteMapBuilder()
    builder.add_pages(site_map.pages)
    builder._start_url = start_url
    report_path = ""
    try:
        from pathlib import Path

        report_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
        report_file = str(report_dir / "sitemap_report.md")
        builder.generate_report(output_path=report_file)
        report_path = report_file
    except Exception as e:
        logger.warning("report_generation_failed", error=str(e))

    # Optionally generate tests
    test_gen_summary: CrawlTestGenSummary | None = None
    if request.generate_tests:
        try:
            generator = CrawlTestGenerator(crawl_results)
            generated_files = await generator.generate_all()

            pom_count = sum(1 for f in generated_files if "/pages/" in f)
            test_count = sum(1 for f in generated_files if "/tests/" in f)

            test_gen_summary = CrawlTestGenSummary(
                pom_files_generated=pom_count,
                test_files_generated=test_count,
                total_files=len(generated_files),
                output_directory=str(generator._output_dir),
            )

            logger.info(
                "crawl_test_generation_completed",
                pom_files=pom_count,
                test_files=test_count,
            )
        except Exception as e:
            logger.error("crawl_test_generation_failed", error=str(e))

    # Build page summaries
    page_summaries = [
        CrawlPageSummary(
            url=page.url,
            title=page.title,
            depth=page.depth,
            elements_count=len(page.elements),
            links_count=len(page.links),
            has_screenshot=bool(page.screenshot_path),
        )
        for page in site_map.pages
    ]

    duration = time.time() - start_time

    # Determine status
    status = "completed"
    if crawl_results.errors and site_map.total_pages > 0:
        status = "partial"
    elif site_map.total_pages == 0:
        status = "failed"

    logger.info(
        "crawl_endpoint_completed",
        url=start_url,
        status=status,
        pages=site_map.total_pages,
        duration=round(duration, 2),
    )

    return CrawlResponse(
        status=status,
        start_url=start_url,
        total_pages=site_map.total_pages,
        max_depth_reached=site_map.max_depth_reached,
        pages=page_summaries,
        suggested_flows=crawl_results.suggested_flows,
        errors=crawl_results.errors,
        test_generation=test_gen_summary,
        report_path=report_path,
        duration_seconds=round(duration, 2),
    )
