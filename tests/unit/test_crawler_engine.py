"""Unit tests for crawler engine with mocked Playwright."""

import pytest

from src.crawler.config import CrawlConfig


class TestCrawlConfig:
    """Tests for CrawlConfig dataclass."""

    @pytest.mark.unit
    def test_default_config_values(self):
        """Verify default configuration values."""
        config = CrawlConfig()
        assert config.max_depth == 3
        assert config.max_pages == 50
        assert config.timeout_per_page == 10000
        assert config.headless is True
        assert config.browser == "chromium"
        assert config.extract_elements is True
        assert config.screenshot_pages is True
        assert config.respect_robots_txt is True

    @pytest.mark.unit
    def test_is_excluded_matches_patterns(self):
        """Verify URL exclusion patterns work."""
        config = CrawlConfig()
        assert config.is_excluded("https://example.com/image.png")
        assert config.is_excluded("https://example.com/file.pdf")
        assert config.is_excluded("https://example.com/style.css")
        assert config.is_excluded("https://example.com/logout")
        assert not config.is_excluded("https://example.com/dashboard")
        assert not config.is_excluded("https://example.com/login")

    @pytest.mark.unit
    def test_is_excluded_fragment_urls(self):
        """Verify fragment/hash URLs are excluded."""
        config = CrawlConfig()
        assert config.is_excluded("https://example.com/page#section")

    @pytest.mark.unit
    def test_is_excluded_javascript_urls(self):
        """Verify javascript: and mailto: URLs are excluded."""
        config = CrawlConfig()
        assert config.is_excluded("javascript:void(0)")
        assert config.is_excluded("mailto:user@example.com")

    @pytest.mark.unit
    def test_is_allowed_domain_empty_allows_all(self):
        """Verify empty allowed_domains permits all domains."""
        config = CrawlConfig(allowed_domains=[])
        assert config.is_allowed_domain("https://any-site.com/page")

    @pytest.mark.unit
    def test_is_allowed_domain_restricts(self):
        """Verify allowed_domains filters correctly."""
        config = CrawlConfig(allowed_domains=["example.com"])
        assert config.is_allowed_domain("https://example.com/page")
        assert config.is_allowed_domain("https://sub.example.com/page")
        assert not config.is_allowed_domain("https://other.com/page")

    @pytest.mark.unit
    def test_custom_exclude_patterns(self):
        """Verify custom exclude patterns override defaults."""
        config = CrawlConfig(exclude_patterns=[r".*admin.*"])
        assert config.is_excluded("https://example.com/admin/panel")
        assert not config.is_excluded("https://example.com/image.png")


class TestCrawlerEngineURLNormalization:
    """Tests for URL normalization logic."""

    @pytest.mark.unit
    def test_normalize_removes_fragment(self):
        from src.crawler.engine import CrawlerEngine

        engine = CrawlerEngine.__new__(CrawlerEngine)
        assert engine._normalize_url("https://example.com/page#section") == "https://example.com/page"

    @pytest.mark.unit
    def test_normalize_removes_trailing_slash(self):
        from src.crawler.engine import CrawlerEngine

        engine = CrawlerEngine.__new__(CrawlerEngine)
        assert engine._normalize_url("https://example.com/page/") == "https://example.com/page"

    @pytest.mark.unit
    def test_normalize_lowercases_host(self):
        from src.crawler.engine import CrawlerEngine

        engine = CrawlerEngine.__new__(CrawlerEngine)
        normalized = engine._normalize_url("https://Example.COM/Page")
        assert "example.com" in normalized

    @pytest.mark.unit
    def test_normalize_root_path(self):
        from src.crawler.engine import CrawlerEngine

        engine = CrawlerEngine.__new__(CrawlerEngine)
        assert engine._normalize_url("https://example.com") == "https://example.com/"
        assert engine._normalize_url("https://example.com/") == "https://example.com/"
