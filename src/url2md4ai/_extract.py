"""Main-content extraction: trafilatura with a precision-first fallback chain.

This is the only module that knows about the extraction backend, so swapping
trafilatura for another extractor never touches the rest of the package.
"""

import json
from collections.abc import Iterator

import trafilatura
from lxml import etree
from lxml import html as lxml_html

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

    # JS-only pages (SPAs) often still ship their content as JSON-LD for SEO.
    result = _jsonld_markdown(content)
    if result and len(result) >= MIN_CHARS:
        return result, "jsonld"

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


def _jsonld_markdown(content: bytes | str) -> str | None:
    """Render the page's JSON-LD structured data (if any) as Markdown."""
    try:
        tree = lxml_html.fromstring(content)
    except (etree.ParserError, ValueError):
        return None

    sections = []
    for script in tree.xpath('//script[@type="application/ld+json"]/text()'):
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            continue
        sections.extend(filter(None, (_jsonld_section(obj) for obj in _iter_jsonld(data))))
    return "\n\n".join(sections) or None


def _iter_jsonld(data: object) -> Iterator[dict]:
    """Yield every JSON-LD object, unwrapping top-level lists and @graph."""
    if isinstance(data, dict):
        yield data
        yield from _iter_jsonld(data.get("@graph", []))
    elif isinstance(data, list):
        for item in data:
            yield from _iter_jsonld(item)


def _jsonld_section(obj: dict) -> str | None:
    """One Markdown section per JSON-LD object that carries real text."""
    body = obj.get("description") or obj.get("articleBody")
    if not isinstance(body, str) or not body.strip():
        return None
    if "<" in body:  # description fields may legally contain HTML
        wrapped = f"<html><body><article>{body}</article></body></html>"
        extracted = trafilatura.extract(wrapped, favor_recall=True, **_BASE_OPTIONS)
        body = (extracted or trafilatura.html2txt(wrapped)).strip()

    title = next(
        (obj[key] for key in ("title", "name", "headline") if isinstance(obj.get(key), str)),
        None,
    )
    return f"# {title.strip()}\n\n{body}" if title else body
