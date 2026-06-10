# url2md4ai

Convert any URL into clean, **token-efficient Markdown for LLMs**. One thing, done well.

```bash
uv tool install url2md4ai   # or: pip install url2md4ai
url2md4ai https://en.wikipedia.org/wiki/Markdown
```

Feed web pages to an LLM without paying for navigation menus, cookie banners, ads, footers and tracking scripts. url2md4ai fetches a page, extracts the main content and emits structured Markdown — headings, text, tables, lists, code blocks, image alt text — typically cutting raw page size by **>90%**.

```markdown
---
title: "Markdown - Wikipedia"
source: https://en.wikipedia.org/wiki/Markdown
fetched: 2026-06-10
---

# Markdown

**Markdown** is a lightweight markup language for creating formatted text...
```

## ⚠️ 2.0 is a complete rewrite

Version 2.0 starts from scratch with a radically smaller scope and footprint:

- **2 runtime dependencies** ([trafilatura](https://github.com/adbar/trafilatura) + [httpx](https://github.com/encode/httpx)) — down from 12. No more Playwright, OpenAI, pandas or aiohttp.
- **Static fetching only.** No JavaScript rendering, no headless browser. If you need to render SPAs, pair it with your own renderer and call `html_to_markdown()`.
- **New, minimal API.** The 0.x API is gone.

## Usage

### CLI (humans & scripts)

```bash
url2md4ai https://example.com/article            # markdown on stdout
url2md4ai --no-links https://example.com/article # drop link URLs, keep text (saves tokens)
url2md4ai --no-frontmatter https://example.com   # body only
url2md4ai -v https://example.com                 # extraction strategy on stderr
url2md4ai --raw https://example.com              # raw extractor output (debugging)
```

### MCP server (agents)

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

The server exposes a single tool, `url_to_markdown(url, include_links=true)`.

### Python library

```python
from url2md4ai import to_markdown, html_to_markdown

md = to_markdown("https://example.com/article")
md = to_markdown("https://example.com/article", include_links=False, timeout=30)

# already have the HTML? (cache, your own renderer, ...)
md = html_to_markdown(html, base_url="https://example.com/article")
```

Errors are explicit and typed: `FetchError` (network / HTTP status), `UnsupportedContentError` (PDF, images, JSON...), `ExtractionError` (empty, paywalled or JS-only pages) — all subclasses of `Url2md4aiError`.

## How it works

1. **Fetch** — plain HTTP GET (httpx, redirects followed, 10 MB cap). Markdown/plain-text responses are returned as-is; PDFs and other binaries fail fast with a clear error.
2. **Extract** — [trafilatura](https://github.com/adbar/trafilatura), precision-first: best-in-class boilerplate removal in independent benchmarks. If precision mode finds too little, it retries favoring recall, then reads the page's JSON-LD structured data (many SPAs — job boards, e-commerce — ship their content there for SEO), then falls back to whole-page text before giving up.
3. **Post-process** — whitespace normalization, decorative images without alt text dropped, optional link stripping (informative images and alt text always survive), YAML frontmatter (`title`, `source`, `fetched`).

## Philosophy

- **One thing well**: URL → LLM-ready Markdown. No crawling, no screenshots, no LLM calls, no browser.
- **Token efficiency is the metric**: every byte in the output should inform the model.
- **Boring, maintainable code**: small pure functions, typed end to end, offline test suite.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check && uv run ruff format --check
```

## License

[MIT](LICENSE)
