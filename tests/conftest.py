"""Shared test helpers: fixture loading and the offline HTTP transport seam."""

from pathlib import Path

import httpx
import pytest

import url2md4ai._fetch as _fetch

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


@pytest.fixture
def serve(monkeypatch):
    """Route HTTP requests to canned responses, with no network access.

    Usage: ``serve({url: (status, content_type, body)})``. Unknown URLs get 404.
    """

    def _serve(routes: dict[str, tuple[int, str, bytes | str]]) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            route = routes.get(str(request.url))
            if route is None:
                return httpx.Response(404)
            status, content_type, body = route
            return httpx.Response(
                status,
                headers={"content-type": content_type},
                content=body.encode() if isinstance(body, str) else body,
            )

        monkeypatch.setattr(_fetch, "_transport", httpx.MockTransport(handler))

    return _serve


@pytest.fixture
def serve_fixture(serve):
    """Serve a fixture file at a URL: ``url = serve_fixture("article.html")``."""

    def _serve_fixture(name: str, content_type: str = "text/html") -> str:
        url = f"https://test.example/{name}"
        serve({url: (200, content_type, load_fixture(name))})
        return url

    return _serve_fixture
