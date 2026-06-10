"""Optional JavaScript rendering via Playwright (the ``js`` extra).

Used as a last-resort fallback for pages whose content only exists after
client-side rendering. The import is lazy so the core package works without
Playwright installed.
"""

import contextlib

from ._exceptions import FetchError

INSTALL_HINT = 'install the js extra: pip install "url2md4ai[js]" && playwright install chromium'

# Resource types that cost time and bandwidth but never carry text content.
_SKIPPED_RESOURCES = frozenset({"image", "media", "font"})

# Iframes with less rendered markup than this are trackers/pixels, not content.
_MIN_FRAME_HTML = 500


def available() -> bool:
    """True when Playwright is importable (the ``js`` extra is installed)."""
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return False
    return True


def render_page(url: str, *, timeout: float, user_agent: str | None = None) -> str:
    """Load ``url`` in headless Chromium and return the rendered HTML."""
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise FetchError(f"JavaScript rendering is not available — {INSTALL_HINT}") from exc

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(**({"user_agent": user_agent} if user_agent else {}))
                page.route(
                    "**/*",
                    lambda route: (
                        route.abort()
                        if route.request.resource_type in _SKIPPED_RESOURCES
                        else route.continue_()
                    ),
                )
                # Late trackers often keep the network busy past the timeout;
                # in that case use whatever has rendered so far.
                with contextlib.suppress(PlaywrightTimeout):
                    page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
                return _merged_content(page, PlaywrightError)
            finally:
                browser.close()
    except PlaywrightError as exc:
        raise FetchError(f"JavaScript rendering of {url} failed: {exc}") from exc


def _merged_content(page, playwright_error: type[Exception]) -> str:
    """Page HTML with content-bearing iframes inlined.

    ``page.content()`` only covers the main frame, but pages routinely mount
    their real content in an embedded iframe (job boards, checkout widgets,
    documentation viewers), so each substantial child frame is appended to
    the document body.
    """
    html = page.content()
    frame_bodies = []
    for frame in page.frames:
        if frame is page.main_frame:
            continue
        try:
            body = frame.evaluate("document.body ? document.body.innerHTML : ''")
        except playwright_error:
            continue  # cross-origin or already-detached frames are best-effort
        if body and len(body) >= _MIN_FRAME_HTML:
            frame_bodies.append(f"<section>{body}</section>")
    if not frame_bodies:
        return html
    merged = "\n".join(frame_bodies)
    if "</body>" in html:
        return html.replace("</body>", f"{merged}</body>", 1)
    return html + merged
