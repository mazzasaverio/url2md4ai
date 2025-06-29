"""URL to Markdown converter with LLM optimization."""

import asyncio
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
import html2text
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

try:
    import trafilatura

    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

from .config import Config
from .utils import get_logger
from .utils.rate_limiter import SimpleCache


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
        if not TRAFILATURA_AVAILABLE:
            self.logger.warning(
                "Trafilatura not available, falling back to BeautifulSoup",
            )
            return None

        try:
            extracted = trafilatura.extract(
                html_content,
                url=url,
                include_comments=self.config.include_comments,
                include_tables=self.config.include_tables,
                include_images=self.config.include_images,
                include_formatting=self.config.include_formatting,
                favor_precision=self.config.favor_precision,
                favor_recall=self.config.favor_recall,
            )

            if extracted and self.config.llm_optimized:
                return self._post_process_for_llm(str(extracted))

            return str(extracted) if extracted else None

        except Exception as e:
            self.logger.debug(f"Trafilatura extraction failed: {e}")
            return None

    def clean_with_beautifulsoup(self, html_content: str) -> str:
        """Fallback content cleaning with BeautifulSoup."""
        soup = BeautifulSoup(html_content, "lxml")

        if self.config.clean_content:
            soup = self._remove_unwanted_elements(soup)

        # Convert to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = not self.config.include_images
        h.body_width = 0
        h.unicode_snob = True
        h.ignore_tables = not self.config.include_tables

        markdown = h.handle(str(soup))

        if self.config.llm_optimized:
            markdown = self._post_process_for_llm(markdown)

        return markdown

    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove unwanted HTML elements based on configuration."""

        # Define unwanted selectors based on config
        unwanted_selectors = []

        if self.config.remove_cookie_banners:
            unwanted_selectors.extend(
                [
                    '[id*="cookie"]',
                    '[class*="cookie"]',
                    '[id*="consent"]',
                    '[class*="consent"]',
                    '[id*="gdpr"]',
                    '[class*="gdpr"]',
                    '[id*="cookiebot"]',
                    '[class*="cookiebot"]',
                    '[id*="privacy"]',
                    '[class*="privacy"]',
                ],
            )

        if self.config.remove_navigation:
            unwanted_selectors.extend(
                [
                    "nav",
                    "header",
                    "footer",
                    '[role="navigation"]',
                    '[role="banner"]',
                    '[role="contentinfo"]',
                    ".navbar",
                    ".header",
                    ".footer",
                    ".sidebar",
                    ".menu",
                ],
            )

        if self.config.remove_ads:
            unwanted_selectors.extend(
                [
                    '[id*="ad"]',
                    '[class*="ad"]',
                    '[id*="advertising"]',
                    '[class*="advertising"]',
                    '[id*="sponsor"]',
                    '[class*="sponsor"]',
                    ".advertisement",
                    ".ad-container",
                ],
            )

        if self.config.remove_social_media:
            unwanted_selectors.extend(
                [
                    '[class*="share"]',
                    '[class*="social"]',
                    '[id*="share"]',
                    '[id*="social"]',
                    ".social-media",
                    ".sharing-buttons",
                ],
            )

        if self.config.remove_comments:
            unwanted_selectors.extend(
                [
                    '[class*="comment"]',
                    '[id*="comment"]',
                    ".comments-section",
                    ".discussion",
                ],
            )

        # Always remove these
        unwanted_selectors.extend(["script", "style", "noscript"])

        # Remove unwanted elements
        for selector in unwanted_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    element.decompose()
            except Exception as e:
                self.logger.debug(f"Error removing selector {selector}: {e}")

        # Remove elements with high cookie keyword density
        if self.config.remove_cookie_banners:
            self._remove_cookie_heavy_content(soup)

        return soup

    def _remove_cookie_heavy_content(self, soup: BeautifulSoup) -> None:
        """Remove elements that are heavily cookie-related."""
        cookie_keywords = [
            "cookie",
            "consent",
            "gdpr",
            "privacy policy",
            "tracking",
            "necessary cookies",
            "marketing cookies",
            "analytics cookies",
            "cookiebot",
            "cookie policy",
            "cookie consent",
            "data processing",
            "third party",
            "advertising partners",
            "personalization",
        ]

        for element in soup.find_all(["div", "section", "article", "p"]):
            if element.get_text():
                text_content = element.get_text().lower()
                if len(text_content) > 50:  # Only check substantial text blocks
                    cookie_mentions = sum(
                        1 for keyword in cookie_keywords if keyword in text_content
                    )
                    density = cookie_mentions / len(text_content.split()) * 100

                    # Remove if high cookie keyword density
                    if cookie_mentions >= 3 or density > 5:
                        element.decompose()

    def _post_process_for_llm(self, content: str) -> str:
        """Post-process content for LLM consumption."""

        # Remove cookie banner text patterns
        cookie_patterns = [
            r"We use cookies.*?privacy policy\.?",
            r"This website uses cookies.*?more information\.?",
            r"By continuing to use.*?cookies\.?",
            r"Accept.*?cookies.*?deny.*?cookies",
            r"Cookie consent.*?necessary.*?marketing.*?analytics",
            r"Cookies are small text files.*?customized\.?",
        ]

        for pattern in cookie_patterns:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE | re.DOTALL)

        # Clean up extra whitespace
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)  # Max 2 consecutive newlines
        content = re.sub(r"[ \t]+", " ", content)  # Normalize spaces

        # Remove lines that are purely cookie/privacy related
        lines = content.split("\n")
        filtered_lines = []

        for line in lines:
            line_lower = line.lower().strip()
            if len(line_lower) < 10:  # Keep short lines
                filtered_lines.append(line)
                continue

            # Skip lines that are predominantly about cookies/privacy
            cookie_score = sum(
                1
                for word in ["cookie", "consent", "gdpr", "privacy", "tracking"]
                if word in line_lower
            )
            word_count = len(line_lower.split())

            if (
                word_count > 5 and cookie_score / word_count < 0.3
            ):  # Less than 30% cookie words
                filtered_lines.append(line)
            elif word_count <= 5:  # Short lines pass through
                filtered_lines.append(line)

        content = "\n".join(filtered_lines)

        # Final cleanup
        return content.strip()


class URLToMarkdownConverter:
    """Main converter class for URL to Markdown conversion with LLM optimization."""

    def __init__(self, config: Config | None = None):
        """Initialize the converter with configuration."""
        self.config = config or Config.from_env()
        self.logger = get_logger(__name__)
        self.cache = SimpleCache() if self.config.enable_caching else None
        self.cleaner = ContentCleaner(self.config)

        self.logger.info("Converter initialized with config")
        if not TRAFILATURA_AVAILABLE and self.config.use_trafilatura:
            self.logger.warning(
                "Trafilatura not available, using BeautifulSoup fallback",
            )

    async def convert_url(
        self,
        url: str,
        output_path: str | None = None,
        use_javascript: bool | None = None,
        use_trafilatura: bool | None = None,
    ) -> ConversionResult:
        """Convert URL to markdown with LLM optimization."""

        if not self._is_valid_url(url):
            return ConversionResult.error_result("Invalid URL format", url)

        start_time = datetime.now()
        self.logger.info(f"Starting conversion: {url}")

        # Check cache first
        if self.cache:
            cached = self.cache.get_url_conversion(url)
            if cached:
                self.logger.info("Returning cached result")
                return cached

        try:
            # Determine extraction method
            use_js = (
                use_javascript
                if use_javascript is not None
                else self.config.javascript_enabled
            )
            use_traff = (
                use_trafilatura
                if use_trafilatura is not None
                else self.config.use_trafilatura
            )

            # Fetch content
            html_content, metadata = await self._fetch_content(url, use_js)

            if not html_content:
                return ConversionResult.error_result("Failed to fetch content", url)

            # Extract content
            if use_traff and TRAFILATURA_AVAILABLE:
                markdown = self.cleaner.clean_with_trafilatura(html_content, url)
                extraction_method = "trafilatura"
                if not markdown:
                    self.logger.info(
                        "Trafilatura failed, falling back to BeautifulSoup",
                    )
                    markdown = self.cleaner.clean_with_beautifulsoup(html_content)
                    extraction_method = "beautifulsoup_fallback"
            else:
                markdown = self.cleaner.clean_with_beautifulsoup(html_content)
                extraction_method = "beautifulsoup"

            if not markdown:
                return ConversionResult.error_result("Content extraction failed", url)

            # Extract title
            soup = BeautifulSoup(html_content, "lxml")
            title_elem = soup.find("title")
            title = title_elem.get_text().strip() if title_elem else ""

            # Generate filename
            if self.config.use_hash_filenames:
                filename = URLHasher.generate_filename(url)
            else:
                # Use title-based filename as fallback
                safe_title = re.sub(r"[^\w\s-]", "", title)[:50]
                filename = (
                    f"{safe_title.replace(' ', '_')}.md"
                    if safe_title
                    else URLHasher.generate_filename(url)
                )

            # Save to file if requested
            save_path = None
            if output_path or self.config.output_dir:
                save_path = output_path or str(Path(self.config.output_dir) / filename)
                self._save_markdown(markdown, save_path)
                self.logger.info(f"Markdown saved to: {save_path}")

            # Create result
            result = ConversionResult.success_result(
                markdown=markdown,
                url=url,
                title=title,
                filename=filename,
                output_path=save_path,
                file_size=len(markdown),
                processing_time=(datetime.now() - start_time).total_seconds(),
                extraction_method=extraction_method,
                metadata=metadata or {},
            )

            # Cache result
            if self.cache:
                self.cache.set_url_conversion(url, result)

            self.logger.info(
                f"Conversion completed: {len(markdown)} chars via {extraction_method}",
            )
            return result

        except Exception as e:
            self.logger.error(f"Conversion failed for {url}: {e}")
            return ConversionResult.error_result(str(e), url)

    async def _fetch_content(
        self,
        url: str,
        use_javascript: bool,
    ) -> tuple[str, dict[str, Any]]:
        """Fetch content from URL with optional JavaScript rendering."""
        if use_javascript:
            return await self._fetch_with_playwright(url)
        return await self._fetch_with_aiohttp(url)

    async def _fetch_with_playwright(self, url: str) -> tuple[str, dict[str, Any]]:
        """Fetch content using Playwright for JavaScript rendering."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.config.browser_headless)
                page = await browser.new_page()

                # Set user agent
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

                # Extract metadata
                title = await page.title()
                url_final = page.url

                await browser.close()

                metadata = {
                    "title": title,
                    "final_url": url_final,
                    "method": "playwright",
                }

                return html_content, metadata

        except Exception as e:
            self.logger.error(f"Playwright fetch failed for {url}: {e}")
            return "", {}

    async def _fetch_with_aiohttp(self, url: str) -> tuple[str, dict[str, Any]]:
        """Fetch content using aiohttp for fast static content."""
        try:
            headers = {"User-Agent": self.config.user_agent}
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)

            async with aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        metadata = {
                            "status": response.status,
                            "content_type": response.headers.get("content-type", ""),
                            "final_url": str(response.url),
                            "method": "aiohttp",
                        }
                        return html_content, metadata
                    self.logger.error(f"HTTP {response.status} for {url}")
                    return "", {}

        except Exception as e:
            self.logger.error(f"Aiohttp fetch failed for {url}: {e}")
            return "", {}

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
