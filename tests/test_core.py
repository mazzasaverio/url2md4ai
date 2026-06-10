"""End-to-end through the public API, with the HTTP layer mocked."""

import pytest
from conftest import load_fixture

from url2md4ai import FetchError, html_to_markdown, to_markdown


def test_article_end_to_end(serve_fixture):
    url = serve_fixture("article.html")
    md = to_markdown(url)
    assert md.startswith("---\n")
    assert 'title: "Designing Resilient Data Pipelines"' in md
    assert f"source: {url}" in md
    assert "fetched: " in md
    assert "Idempotency first" in md
    assert "Sign in" not in md
    assert "All rights reserved" not in md


def test_tables_survive(serve_fixture):
    md = to_markdown(serve_fixture("tables.html"))
    assert "| 404 | Not Found |" in md
    assert "4xx — client errors" in md


def test_image_alt_text_survives(serve_fixture):
    md = to_markdown(serve_fixture("images.html"))
    assert "turquoise water surrounded by dolomite peaks" in md


def test_boilerplate_heavy_page(serve_fixture):
    md = to_markdown(serve_fixture("boilerplate.html"))
    assert "scheduled database upgrade" in md
    assert "Accept all cookies" not in md
    assert "Subscribe to our newsletter" not in md
    assert "three months free" not in md


def test_markdown_served_verbatim(serve_fixture):
    url = serve_fixture("plain.md", content_type="text/markdown")
    md = to_markdown(url)
    assert "VERBATIM-MARKER-DO-NOT-EXTRACT" in md
    assert "race condition in the scheduler" in md
    assert md.startswith("---\n")  # our frontmatter is still prepended


def test_no_links_drops_urls_keeps_images(serve_fixture):
    url = serve_fixture("plain.md", content_type="text/markdown")
    md = to_markdown(url, include_links=False)
    assert "[changelog](" not in md
    assert "changelog" in md


def test_no_frontmatter(serve_fixture):
    md = to_markdown(serve_fixture("article.html"), frontmatter=False)
    assert not md.startswith("---")
    assert "Idempotency first" in md


def test_fetch_error_propagates(serve):
    serve({})
    with pytest.raises(FetchError):
        to_markdown("https://test.example/missing")


def test_html_to_markdown_offline():
    md = html_to_markdown(load_fixture("article.html"), base_url="https://test.example/a")
    assert "Idempotency first" in md
    assert "source: https://test.example/a" in md
