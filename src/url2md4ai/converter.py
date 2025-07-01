"""URL to Markdown converter with LLM optimization."""

import asyncio
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import trafilatura
from playwright.async_api import async_playwright

from .config import Config
from .utils import get_logger


@dataclass
class ConversionResult:
    """Result of URL to markdown conversion."""

    success: bool
    url: str
    markdown: str = ""
    title: str = ""
    filename: str = ""
    output_path: str = ""
    file_size: int = 0
    processing_time: float = 0.0
    extraction_method: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    @classmethod
    def success_result(cls, **kwargs: Any) -> "ConversionResult":
        """Create a successful conversion result."""
        return cls(success=True, **kwargs)

    @classmethod
    def error_result(cls, error: str, url: str) -> "ConversionResult":
        """Create an error conversion result."""
        return cls(success=False, error=error, url=url)


class URLHasher:
    """Generate hash-based filenames for URLs."""

    @staticmethod
    def generate_filename(url: str, extension: str = ".md") -> str:
        """Generate a hash-based filename from URL."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        return f"{url_hash}{extension}"

    @staticmethod
    def generate_hash(url: str) -> str:
        """Generate just the hash part for a URL."""
        return hashlib.sha256(url.encode()).hexdigest()[:16]


class ContentCleaner:
    """Advanced content cleaning for LLM optimization."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(__name__)

    def clean_with_trafilatura(self, html_content: str, url: str) -> str | None:
        """Extract clean content using trafilatura."""

        try:
            extracted = trafilatura.extract(
                html_content,
                url=url,
            )
            return str(extracted) if extracted else None

        except Exception as e:
            self.logger.debug(f"Trafilatura extraction failed: {e}")
            return None


class URLToMarkdownConverter:
    """Main converter class for URL to Markdown conversion with LLM optimization."""

    def __init__(self, config: Config | None = None):
        """Initialize the converter with configuration."""
        self.config = config or Config.from_env()
        self.logger = get_logger(__name__)
        self.cleaner = ContentCleaner(self.config)

    async def convert_url(
        self,
        url: str,
        output_path: str | None = None,
    ) -> ConversionResult:
        """Convert URL to markdown with LLM optimization."""

        if not self._is_valid_url(url):
            return ConversionResult.error_result("Invalid URL format", url)

        try:
            html_content = await self._fetch_content(url)

            if not html_content:
                return ConversionResult.error_result("Failed to fetch content", url)

            markdown = self.cleaner.clean_with_trafilatura(html_content, url)

            if not markdown:
                return ConversionResult.error_result("Content extraction failed", url)

            filename = URLHasher.generate_filename(url)

            save_path = None
            if output_path or self.config.output_dir:
                save_path = output_path or str(Path(self.config.output_dir) / filename)
                self._save_markdown(markdown, save_path)
                self.logger.info(f"Markdown saved to: {save_path}")
            else:
                self.logger.info(f"Markdown saved to: {filename}")

            return ConversionResult.success_result(
                markdown=markdown,
                html_content=html_content,
                url=url,
                filename=filename,
                output_path=save_path or "",
            )

        except Exception as e:
            self.logger.error(f"Conversion failed for {url}: {e}")
            return ConversionResult.error_result(str(e), url)

    async def _fetch_content(
        self,
        url: str,
    ) -> str:
        """Fetch content from URL with optional JavaScript rendering."""
        return await self._fetch_with_playwright(url)

    async def _fetch_with_playwright(self, url: str) -> str:
        """Fetch content using Playwright for JavaScript rendering."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.config.browser_headless)
                page = await browser.new_page()

                await page.set_extra_http_headers(
                    {"User-Agent": self.config.user_agent},
                )

                # Navigate and wait for content
                if self.config.wait_for_network_idle:
                    await page.goto(
                        url,
                        wait_until="networkidle",
                        timeout=self.config.timeout * 1000,
                    )
                else:
                    await page.goto(url, timeout=self.config.timeout * 1000)

                # Additional wait for dynamic content
                if self.config.page_wait_timeout > 0:
                    await page.wait_for_timeout(self.config.page_wait_timeout)

                html_content = await page.content()

                await browser.close()

                return html_content

        except Exception as e:
            self.logger.error(f"Playwright fetch failed for {url}: {e}")
            return ""

    def _save_markdown(self, markdown: str, output_path: str) -> None:
        """Save markdown content to file."""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(markdown, encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Failed to save markdown: {e}")
            raise

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        return url.startswith(("http://", "https://")) and len(url) > 10

    def convert_url_sync(self, url: str, **kwargs: Any) -> ConversionResult:
        """Synchronous wrapper for convert_url."""
        return asyncio.run(self.convert_url(url, **kwargs))
