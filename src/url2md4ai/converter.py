"""URL to Markdown converter with LLM optimization."""

# mypy: ignore-errors

import asyncio
import hashlib
import re
import urllib.parse
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

import trafilatura
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from .config import Config
from .utils import get_logger


class ContentExtractor:
    """Extract clean content from URLs in both HTML and Markdown formats."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config.from_env()
        self.logger = get_logger(__name__)

    def generate_filename(self, url: str, extension: str = ".md") -> str:
        """Generate a filename from URL.

        If `config.use_hash_filenames` is True → keep current deterministic hash.
        Otherwise → create a readable slug from the URL path (domain + last path
        segment) and fall back to hash on collision/edge-cases.
        """

        date_prefix = datetime.now(timezone.utc).strftime("%Y%m%d")

        if self.config.use_hash_filenames:
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            return f"{date_prefix}-{url_hash}{extension}"

        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.replace(".", "-")
        # take last non-empty path segment to avoid extremely long names
        path_seg = parsed.path.rstrip("/").split("/")[-1] or "index"
        slug = self._slugify(f"{netloc}-{path_seg}")

        # ensure length <= 80 chars
        slug = slug[:80]
        if not slug:
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            slug = url_hash

        return f"{date_prefix}-{slug}{extension}"

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
            # Optionally clean up noisy elements before extraction
            if self.config.clean_content:
                html_content = self._clean_html(html_content)

            markdown = trafilatura.extract(
                html_content,
                url=url,
                favor_precision=self.config.favor_precision,
                favor_recall=self.config.favor_recall,
                include_tables=self.config.include_tables,
                include_images=self.config.include_images,
                include_comments=self.config.include_comments,
                include_formatting=self.config.include_formatting,
            )
            if not markdown:
                return None

            # Post-process markdown: normalize blank lines
            markdown = self._normalize_newlines(markdown)

            # Remove lines containing unwanted phrases
            markdown = self._post_filter_markdown(markdown)

            # Try to enrich with generic tables or grid-based data
            table_md = self._extract_structured_tables(html_content)
            if table_md:
                markdown += "\n\n" + table_md

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

    def _clean_html(self, html: str) -> str:
        """Remove common noise elements (cookie banners, ads, nav, etc.)."""

        soup = BeautifulSoup(html, "lxml")

        # Remove cookie banners
        if self.config.remove_cookie_banners:
            selectors = [
                "#CybotCookiebotDialog",
                "[id*=cookie]",
                "[class*=cookie]",
            ]
            for sel in selectors:
                for tag in soup.select(sel):
                    tag.decompose()

        # Remove navigation bars
        if self.config.remove_navigation:
            for tag in soup.find_all("nav"):
                tag.decompose()

        # Remove footer sections
        for tag in soup.find_all("footer"):
            tag.decompose()

        # Additional clean-ups can be added here

        return str(soup)

    # ---------- Helpers ----------

    @staticmethod
    def _normalize_newlines(text: str) -> str:
        """Collapse sequences of 3+ newlines to just two."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Strip trailing spaces
        text = "\n".join(line.rstrip() for line in text.split("\n"))
        # Collapse
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    def _extract_structured_tables(self, html: str) -> str:
        """Return Markdown for any detectable table-like structures.

        1. True HTML <table> → via pandas.read_html
        2. CSS grid / list of repeated spans with classes ending in "bold" →
           heuristic conversion.
        """
        try:
            import pandas as pd
        except ImportError:
            return ""

        dfs: list[pd.DataFrame] = []
        try:
            dfs = pd.read_html(StringIO(html))
        except ValueError:
            # No tables found
            return ""
        except Exception:
            return ""

        md_parts: list[str] = []
        for df in dfs:
            if df.empty or df.shape[1] < 2:
                continue
            md_text = df.to_markdown(index=False) or ""
            if md_text:
                md_parts.append(md_text)

        # Heuristic grid detection if no real tables captured
        if not md_parts:
            grid_table = self._extract_span_groups_table(html)
            if grid_table:
                md_parts.append(grid_table)

        return "\n\n".join(md_parts)

    def _post_filter_markdown(self, text: str) -> str:
        """Remove lines that contain any configured drop phrase."""
        if not self.config.drop_phrases:
            return text
        lines = text.split("\n")
        filtered = [
            ln
            for ln in lines
            if not any(p.lower() in ln.lower() for p in self.config.drop_phrases)
        ]
        return "\n".join(filtered).strip()

    def _slugify(self, text: str) -> str:
        """Simplistic slugify: lowercase, replace non-alnum with dash."""
        text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
        return re.sub(r"-{2,}", "-", text)

    def _extract_span_groups_table(self, html: str) -> str:
        """Detect repeated span groups (bold + siblings) and build a table.

        Works for many job boards/articles that render lists via CSS grids.
        The algorithm:
          • Find all elements with class containing "bold".
          • For each, collect up to 5 following sibling <span> elements.
          • Keep rows where every cell has non-empty text and the row length is
            consistent across at least 3 rows.
        """
        soup = BeautifulSoup(html, "lxml")

        candidates = []

        for bold in soup.select("[class*=bold], b, strong"):
            role_text = bold.get_text(strip=True)
            if not role_text:
                continue

            # Start with direct parent container to traverse siblings at row level
            container = getattr(bold, "parent", bold)
            row_texts = [role_text]

            sibling = getattr(container, "find_next_sibling", lambda: None)()
            while sibling and len(row_texts) < 5:
                # Extract first span or text within this sibling
                cell_text = ""
                if hasattr(sibling, "name") and hasattr(sibling, "get_text"):
                    if getattr(sibling, "name", "") == "span":
                        cell_text = sibling.get_text(strip=True)
                    else:
                        # look for span inside
                        inner_span = getattr(sibling, "find", lambda _: None)("span")
                        if inner_span and hasattr(inner_span, "get_text"):
                            cell_text = inner_span.get_text(strip=True)
                        else:
                            cell_text = sibling.get_text(strip=True)

                if cell_text:
                    row_texts.append(cell_text)

                sibling = getattr(sibling, "find_next_sibling", lambda: None)()

            if len(row_texts) >= 3:  # need at least 3 columns to consider row
                candidates.append(row_texts)

        if len(candidates) < 3:
            return ""

        # Determine dominant column count
        from collections import Counter

        counts = Counter(len(r) for r in candidates)
        cols, _ = counts.most_common(1)[0]
        rows = [r for r in candidates if len(r) == cols][:20]

        if len(rows) < 3 or cols < 2:
            return ""

        header = [f"Col{i+1}" for i in range(cols)]
        md_lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(["---"] * cols) + " |",
        ]
        for r in rows:
            md_lines.append("| " + " | ".join(r) + " |")

        return "\n".join(md_lines)
