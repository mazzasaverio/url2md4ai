"""URL to Markdown converter with LLM optimization."""

import asyncio
import hashlib
from pathlib import Path
from typing import Any

import trafilatura
from playwright.async_api import async_playwright

from .config import Config
from .utils import get_logger


class ContentExtractor:
    """Extract clean content from URLs in both HTML and Markdown formats."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config.from_env()
        self.logger = get_logger(__name__)

    def generate_filename(self, url: str, extension: str = ".md") -> str:
        """Generate a hash-based filename from URL."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        return f"{url_hash}{extension}"

    async def extract_html(self, url: str) -> str | None:
        """Extract raw HTML content from a URL."""
        if not self._is_valid_url(url):
            return None

        try:
            return await self._fetch_content(url)
        except Exception as e:
            self.logger.error(f"HTML extraction failed for {url}: {e}")
            return None

    async def extract_markdown(
        self,
        url: str,
        html_content: str | None = None,
        output_path: str | None = None,
        save_to_file: bool = True,
    ) -> dict[str, Any] | None:
        """Extract clean Markdown from URL or HTML content."""
        if not html_content:
            html_result = await self.extract_html(url)
            if not html_result:
                return None
            html_content = html_result

        try:
            markdown = trafilatura.extract(html_content, url=url)
            if not markdown:
                return None

            filename = self.generate_filename(url)
            save_path = None

            if save_to_file and (output_path or self.config.output_dir):
                try:
                    save_path = output_path or str(
                        Path(self.config.output_dir) / filename,
                    )
                    self._save_markdown(markdown, save_path)
                    self.logger.info(f"Markdown saved to: {save_path}")
                except Exception as e:
                    self.logger.error(f"Failed to save markdown: {e}")
                    save_path = ""  # Clear output_path if save fails

            else:
                self.logger.info(f"Markdown extracted with filename: {filename}")

            return {
                "markdown": markdown,
                "html_content": html_content,
                "url": url,
                "filename": filename,
                "output_path": save_path or "",
            }

        except Exception as e:
            self.logger.error(f"Markdown extraction failed for {url}: {e}")
            return None

    async def _fetch_content(self, url: str) -> str:
        """Fetch raw HTML content from URL."""
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

    def extract_html_sync(self, url: str) -> str | None:
        """Synchronous wrapper for extract_html."""
        return asyncio.run(self.extract_html(url))

    def extract_markdown_sync(
        self,
        url: str,
        html_content: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Synchronous wrapper for extract_markdown."""
        return asyncio.run(self.extract_markdown(url, html_content, **kwargs))
