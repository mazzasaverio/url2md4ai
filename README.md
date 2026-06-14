# url2md4ai

[![PyPI version](https://img.shields.io/pypi/v/url2md4ai)](https://pypi.org/project/url2md4ai/)
[![Python versions](https://img.shields.io/pypi/pyversions/url2md4ai)](https://pypi.org/project/url2md4ai/)
[![CI](https://img.shields.io/github/actions/workflow/status/mazzasaverio/url2md4ai/ci.yml?branch=master)](https://github.com/mazzasaverio/url2md4ai/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/url2md4ai/month)](https://pepy.tech/project/url2md4ai)
[![License: MIT](https://img.shields.io/pypi/l/url2md4ai)](LICENSE)

Convert any URL into clean, token-efficient Markdown for LLMs.

```bash
uv tool install url2md4ai   # or: pip install url2md4ai
url2md4ai https://en.wikipedia.org/wiki/Markdown
```

Feed web pages to an LLM without paying for navigation menus, cookie banners, ads and scripts. url2md4ai fetches a page, extracts the main content and emits structured Markdown (headings, text, tables, lists, code blocks, image alt text), typically cutting raw page size by more than 90%.

```markdown
---
title: "Markdown - Wikipedia"
source: https://en.wikipedia.org/wiki/Markdown
fetched: 2026-06-10
---

# Markdown

**Markdown** is a lightweight markup language for creating formatted text...
```

## CLI

```bash
url2md4ai https://example.com/article            # markdown on stdout
url2md4ai --no-links https://example.com/article # drop link URLs, keep text (saves tokens)
url2md4ai --no-frontmatter https://example.com   # body only
url2md4ai --render https://example.com/spa       # force JavaScript rendering (js extra)
url2md4ai -v https://example.com                 # extraction strategy on stderr
```

## MCP server (for agents)

Install with the `mcp` extra and register the stdio server in your MCP client (Claude Code, Claude Desktop, ...):

```bash
uv tool install "url2md4ai[mcp]"
```

```json
{
  "mcpServers": {
    "url2md4ai": { "command": "url2md4ai-mcp" }
  }
}
```

The server exposes a single tool: `url_to_markdown(url, include_links=true, render=false)`.

## Python library

Add it to your project with `uv add url2md4ai` (or `pip install url2md4ai`):

```python
from url2md4ai import to_markdown, html_to_markdown

md = to_markdown("https://example.com/article")
md = to_markdown("https://example.com/article", include_links=False, timeout=30)

# already have the HTML? (cache, your own renderer, ...)
md = html_to_markdown(html, base_url="https://example.com/article")
```

Errors are explicit and typed: `FetchError` (network / HTTP status), `UnsupportedContentError` (PDF, images, JSON...), `ExtractionError` (empty or paywalled pages), all subclasses of `Url2md4aiError`.

## JavaScript pages

The core package uses static fetching only, which covers most articles, docs and blogs with zero browser overhead. For pages that only exist after client-side rendering, install the `js` extra:

```bash
pip install "url2md4ai[js]"
playwright install chromium
```

- With the extra installed, rendering kicks in automatically when static extraction finds nothing (`render="auto"`, the default).
- Some pages serve partial static content and load the rest client-side (embedded job boards, widgets). No heuristic can detect that reliably, so force rendering when you know you need it: `--render` on the CLI, `render="force"` in Python, `render=true` on the MCP tool.
- Content-bearing iframes are included in the result; tracker frames, images, media and fonts are skipped.

## How it works

1. **Fetch**: plain HTTP GET (httpx, redirects followed, 10 MB cap). Markdown and plain-text responses are returned as-is; PDFs and other binaries fail fast with a clear error.
2. **Extract**: [trafilatura](https://github.com/adbar/trafilatura), precision-first. If precision mode finds too little it retries favoring recall, then reads the page's JSON-LD structured data (many JavaScript-heavy sites ship their content there for SEO), then optionally renders JavaScript, then falls back to whole-page text before giving up.
3. **Post-process**: whitespace normalization, decorative images without alt text dropped, optional link stripping, YAML frontmatter (`title`, `source`, `fetched`).

## Philosophy

- One thing well: URL in, LLM-ready Markdown out. No crawling, no screenshots, no LLM calls.
- Token efficiency is the metric: every byte in the output should inform the model.
- Lean by default: 2 runtime dependencies; browsers and MCP are opt-in extras.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check && uv run ruff format --check
```

## License

[MIT](LICENSE)
