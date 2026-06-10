"""MCP server smoke test (skipped when the optional extra is not installed)."""

import asyncio

import pytest

pytest.importorskip("mcp")

from url2md4ai._mcp import _build_server


def test_tool_is_registered():
    server = _build_server()
    tools = asyncio.run(server.list_tools())
    assert [tool.name for tool in tools] == ["url_to_markdown"]


def test_tool_converts(serve_fixture):
    url = serve_fixture("article.html")
    server = _build_server()
    result, _ = asyncio.run(server.call_tool("url_to_markdown", {"url": url}))
    assert "Idempotency first" in result[0].text
