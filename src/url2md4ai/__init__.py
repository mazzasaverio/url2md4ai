"""url2md4ai: convert any URL into clean, token-efficient Markdown for LLMs.

Public API: :func:`to_markdown`, :func:`html_to_markdown` and the exceptions.
Everything else is private.
"""

import datetime
from typing import Literal

from . import _render
from ._exceptions import (
    ExtractionError,
    FetchError,
    UnsupportedContentError,
    Url2md4aiError,
)
from ._extract import extract_markdown, extract_title
from ._fetch import DEFAULT_TIMEOUT, fetch_page
from ._postprocess import (
    build_frontmatter,
    normalize_whitespace,
    strip_empty_images,
    strip_links,
)

__version__ = "2.1.0"

__all__ = [
    "ExtractionError",
    "FetchError",
    "UnsupportedContentError",
    "Url2md4aiError",
    "html_to_markdown",
    "to_markdown",
]

RenderMode = Literal["auto", "never", "force"]


def to_markdown(
    url: str,
    *,
    include_links: bool = True,
    frontmatter: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
    user_agent: str | None = None,
    render: RenderMode = "auto",
) -> str:
    """Fetch ``url`` and return its main content as LLM-ready Markdown.

    Set ``include_links=False`` to drop link URLs (keeping their text) for
    extra token savings; images and their alt text are always preserved.

    ``render`` controls the JavaScript-rendering fallback (requires the
    ``js`` extra): ``"auto"`` renders only when static extraction finds
    nothing, ``"force"`` always renders, ``"never"`` disables it.
    """
    markdown, _ = _convert_url(
        url,
        include_links=include_links,
        frontmatter=frontmatter,
        timeout=timeout,
        user_agent=user_agent,
        render=render,
    )
    return markdown


def html_to_markdown(
    html: str | bytes,
    *,
    base_url: str | None = None,
    include_links: bool = True,
    frontmatter: bool = True,
) -> str:
    """Convert already-fetched HTML to LLM-ready Markdown (no network access)."""
    markdown, _ = extract_markdown(html, base_url=base_url, include_links=include_links)
    title = extract_title(html, base_url=base_url)
    return _finalize(
        markdown,
        include_links=include_links,
        header=_header(frontmatter, title=title, source=base_url or "unknown"),
    )


def _convert_url(
    url: str,
    *,
    include_links: bool,
    frontmatter: bool,
    timeout: float,
    user_agent: str | None,
    render: RenderMode = "auto",
) -> tuple[str, str]:
    """Shared pipeline returning ``(markdown, strategy)``; used by API, CLI and MCP."""
    if render == "force":
        return _convert_rendered(
            url,
            include_links=include_links,
            frontmatter=frontmatter,
            timeout=timeout,
            user_agent=user_agent,
        )

    page = fetch_page(url, timeout=timeout, user_agent=user_agent)

    if page.text is not None:
        markdown, strategy = page.text, "verbatim"
        title = None
    else:
        try:
            markdown, strategy = extract_markdown(
                page.content, base_url=page.url, include_links=include_links
            )
        except ExtractionError as exc:
            if render == "never":
                raise
            if not _render.available():
                raise ExtractionError(f"{exc} ({_render.INSTALL_HINT})") from exc
            return _convert_rendered(
                page.url,
                include_links=include_links,
                frontmatter=frontmatter,
                timeout=timeout,
                user_agent=user_agent,
            )
        title = extract_title(page.content, base_url=page.url)

    final = _finalize(
        markdown,
        include_links=include_links,
        header=_header(frontmatter, title=title, source=page.url),
    )
    return final, strategy


def _convert_rendered(
    url: str,
    *,
    include_links: bool,
    frontmatter: bool,
    timeout: float,
    user_agent: str | None,
) -> tuple[str, str]:
    """Convert via headless-browser rendering (the ``js`` extra)."""
    html = _render.render_page(url, timeout=timeout, user_agent=user_agent)
    markdown, strategy = extract_markdown(html, base_url=url, include_links=include_links)
    title = extract_title(html, base_url=url)
    final = _finalize(
        markdown,
        include_links=include_links,
        header=_header(frontmatter, title=title, source=url),
    )
    return final, f"render:{strategy}"


def _header(enabled: bool, *, title: str | None, source: str) -> str:
    if not enabled:
        return ""
    return build_frontmatter(title=title, source=source, fetched=datetime.date.today())


def _finalize(markdown: str, *, include_links: bool, header: str) -> str:
    markdown = strip_empty_images(markdown)
    if not include_links:
        markdown = strip_links(markdown)
    return header + normalize_whitespace(markdown)
