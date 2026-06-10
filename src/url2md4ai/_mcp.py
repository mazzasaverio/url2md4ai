"""MCP server exposing the converter to agents over stdio.

Requires the optional ``mcp`` extra: ``pip install "url2md4ai[mcp]"``.
"""

import sys

from . import to_markdown


def _build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit(
            'url2md4ai: the MCP server requires the optional extra: pip install "url2md4ai[mcp]"'
        ) from exc

    server = FastMCP("url2md4ai")

    @server.tool()
    def url_to_markdown(url: str, include_links: bool = True, render: bool = False) -> str:
        """Convert any web page URL to clean, token-efficient Markdown.

        Returns the main content of the page (headings, text, tables, lists,
        code blocks, image alt text) with navigation, ads and other boilerplate
        removed. Set include_links=false to also drop link URLs and save tokens.
        Set render=true to force JavaScript rendering, e.g. when the result
        misses content that the page loads client-side.
        """
        return to_markdown(url, include_links=include_links, render="force" if render else "auto")

    return server


def main() -> int:
    _build_server().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
