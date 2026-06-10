"""HTTP layer: status handling, content-type routing, size cap."""

import pytest

from url2md4ai import FetchError, UnsupportedContentError
from url2md4ai._fetch import fetch_page

URL = "https://test.example/page"


def test_404_raises_fetch_error(serve):
    serve({})
    with pytest.raises(FetchError, match="404"):
        fetch_page(URL)


def test_500_raises_fetch_error(serve):
    serve({URL: (500, "text/html", "boom")})
    with pytest.raises(FetchError, match="500"):
        fetch_page(URL)


def test_403_hints_at_bot_block(serve):
    serve({URL: (403, "text/html", "forbidden")})
    with pytest.raises(FetchError, match="paywall"):
        fetch_page(URL)


def test_pdf_is_unsupported(serve):
    serve({URL: (200, "application/pdf", b"%PDF-1.7")})
    with pytest.raises(UnsupportedContentError, match="application/pdf"):
        fetch_page(URL)


def test_json_is_unsupported(serve):
    serve({URL: (200, "application/json", b"{}")})
    with pytest.raises(UnsupportedContentError):
        fetch_page(URL)


def test_html_goes_to_pipeline(serve):
    serve({URL: (200, "text/html; charset=utf-8", "<html><body>hi</body></html>")})
    page = fetch_page(URL)
    assert page.content_type == "text/html"
    assert page.text is None
    assert b"hi" in page.content


def test_markdown_is_returned_as_text(serve):
    serve({URL: (200, "text/markdown; charset=utf-8", "# Hello")})
    page = fetch_page(URL)
    assert page.text == "# Hello"


def test_oversized_body_is_rejected(serve):
    serve({URL: (200, "text/html", b"x" * (10 * 1024 * 1024 + 1))})
    with pytest.raises(FetchError, match="10 MB"):
        fetch_page(URL)
