"""Main-content extraction: trafilatura with a precision-first fallback chain.

This is the only module that knows about the extraction backend, so swapping
trafilatura for another extractor never touches the rest of the package.
"""

import trafilatura

from ._exceptions import ExtractionError

MIN_CHARS = 150  # below this, an extraction attempt is considered failed

# No `deduplicate`: trafilatura's dedup cache is global across calls (meant for
# crawling), so converting the same URL twice in one process would discard content.
_BASE_OPTIONS = {
    "output_format": "markdown",
    "include_tables": True,
    "include_images": True,
    "include_formatting": True,
    "include_comments": False,
    "with_metadata": False,
}


def extract_markdown(
    content: bytes | str,
    *,
    base_url: str | None = None,
    include_links: bool = True,
) -> tuple[str, str]:
    """Extract the main content of an HTML page as Markdown.

    Returns ``(markdown, strategy)`` where strategy is one of
    ``primary`` / ``recall-retry`` / ``baseline`` (useful for diagnostics).
    Raises ExtractionError when every strategy comes back empty.
    """
    attempts = (
        ("primary", {"favor_precision": True}),
        ("recall-retry", {"favor_recall": True}),
    )
    for strategy, bias in attempts:
        result = trafilatura.extract(
            content, url=base_url, include_links=include_links, **_BASE_OPTIONS, **bias
        )
        if result and len(result) >= MIN_CHARS:
            return result, strategy

    result = trafilatura.html2txt(content)
    if result and len(result.strip()) >= MIN_CHARS:
        return result.strip(), "baseline"

    raise ExtractionError(
        "no extractable content — the page may be empty, paywalled, or require JavaScript rendering"
    )


def extract_title(content: bytes | str, *, base_url: str | None = None) -> str | None:
    """Best-effort page title for the frontmatter; None when unavailable."""
    metadata = trafilatura.extract_metadata(content, default_url=base_url)
    return metadata.title if metadata else None
