"""HTTP layer: fetch a URL and route the response by content type.

The only side effect in the package lives here, behind the module-level
``_transport`` seam so tests can swap in an ``httpx.MockTransport``.
"""

from dataclasses import dataclass

import httpx

from ._exceptions import FetchError, UnsupportedContentError

DEFAULT_TIMEOUT = 15.0
MAX_BODY_BYTES = 10 * 1024 * 1024

ACCEPT = "text/html, application/xhtml+xml;q=0.9, */*;q=0.5"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 url2md4ai/2.0"
)

HTML_TYPES = frozenset({"text/html", "application/xhtml+xml"})
TEXT_TYPES = frozenset({"text/markdown", "text/plain"})

# Test seam: monkeypatched with httpx.MockTransport in the test suite.
_transport: httpx.BaseTransport | None = None


@dataclass(frozen=True)
class FetchedPage:
    """A fetched response, normalized for the extraction pipeline."""

    url: str  # final URL after redirects
    content: bytes  # raw body; trafilatura detects encoding from bytes
    content_type: str  # normalized media type, e.g. "text/html"
    text: str | None  # decoded body iff already markdown/plain text


def fetch_page(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    user_agent: str | None = None,
) -> FetchedPage:
    """Fetch ``url`` and return its body, routed by content type.

    Raises FetchError on network failures and non-2xx responses, and
    UnsupportedContentError for content types we cannot convert (PDF, images...).
    """
    headers = {"Accept": ACCEPT, "User-Agent": user_agent or DEFAULT_USER_AGENT}
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=httpx.Timeout(timeout),
            headers=headers,
            transport=_transport,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        hint = " (the site may block bots or require a login/paywall)" if status == 403 else ""
        raise FetchError(f"GET {url} returned HTTP {status}{hint}") from exc
    except httpx.HTTPError as exc:
        raise FetchError(f"GET {url} failed: {exc}") from exc

    if len(response.content) > MAX_BODY_BYTES:
        raise FetchError(f"GET {url} returned more than {MAX_BODY_BYTES // 1024 // 1024} MB")

    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type and content_type not in HTML_TYPES | TEXT_TYPES:
        raise UnsupportedContentError(
            f"content type '{content_type}' is not convertible; url2md4ai handles HTML pages only"
        )

    return FetchedPage(
        url=str(response.url),
        content=response.content,
        content_type=content_type or "text/html",
        text=response.text if content_type in TEXT_TYPES else None,
    )
