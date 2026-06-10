"""JavaScript-rendering fallback: trigger logic, with the browser mocked out."""

import pytest
from conftest import load_fixture

import url2md4ai._render as _render
from url2md4ai import ExtractionError, to_markdown


@pytest.fixture
def fake_browser(monkeypatch):
    """Pretend the js extra is installed and rendering yields article.html."""
    monkeypatch.setattr(_render, "available", lambda: True)
    monkeypatch.setattr(
        _render,
        "render_page",
        lambda url, *, timeout, user_agent=None: load_fixture("article.html").decode(),
    )


def test_auto_falls_back_to_rendering_on_js_only_pages(serve_fixture, fake_browser):
    md = to_markdown(serve_fixture("js_only.html"))
    assert "Idempotency first" in md


def test_auto_reports_render_strategy(serve_fixture, fake_browser, capsys):
    from url2md4ai._cli import main

    assert main(["-v", serve_fixture("js_only.html")]) == 0
    _, err = capsys.readouterr()
    assert "render:" in err


def test_never_disables_the_fallback(serve_fixture, fake_browser):
    with pytest.raises(ExtractionError):
        to_markdown(serve_fixture("js_only.html"), render="never")


def test_force_skips_static_fetching(fake_browser):
    # No route is served: a static fetch would fail, so force must not fetch.
    md = to_markdown("https://test.example/spa", render="force")
    assert "Idempotency first" in md
    assert "source: https://test.example/spa" in md


def test_auto_without_extra_explains_how_to_install(serve_fixture, monkeypatch):
    monkeypatch.setattr(_render, "available", lambda: False)
    with pytest.raises(ExtractionError, match=r"url2md4ai\[js\]"):
        to_markdown(serve_fixture("js_only.html"))


def test_static_pages_never_trigger_rendering(serve_fixture, monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("render_page must not be called for static pages")

    monkeypatch.setattr(_render, "render_page", explode)
    assert "Idempotency first" in to_markdown(serve_fixture("article.html"))
