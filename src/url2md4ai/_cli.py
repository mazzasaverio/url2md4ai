"""Command-line interface: markdown on stdout, diagnostics on stderr."""

import argparse
import sys

from . import __version__, _convert_url
from ._exceptions import Url2md4aiError
from ._extract import extract_markdown
from ._fetch import DEFAULT_TIMEOUT, fetch_page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="url2md4ai",
        description="Convert any URL into clean, token-efficient Markdown for LLMs.",
    )
    parser.add_argument("url", help="the web page to convert")
    parser.add_argument(
        "--no-links", action="store_true", help="drop link URLs (keep their text) to save tokens"
    )
    parser.add_argument(
        "--no-frontmatter", action="store_true", help="omit the YAML frontmatter header"
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT, metavar="SECONDS", help="HTTP timeout"
    )
    parser.add_argument("--user-agent", metavar="UA", help="override the User-Agent header")
    parser.add_argument(
        "--raw", action="store_true", help="raw extractor output, no post-processing (debugging)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print the extraction strategy on stderr"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        if args.raw:
            markdown, strategy = _convert_raw(args.url, args.timeout, args.user_agent)
        else:
            markdown, strategy = _convert_url(
                args.url,
                include_links=not args.no_links,
                frontmatter=not args.no_frontmatter,
                timeout=args.timeout,
                user_agent=args.user_agent,
            )
    except Url2md4aiError as exc:
        print(f"url2md4ai: error: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"url2md4ai: strategy: {strategy}", file=sys.stderr)
    print(markdown, end="" if markdown.endswith("\n") else "\n")
    return 0


def _convert_raw(url: str, timeout: float, user_agent: str | None) -> tuple[str, str]:
    page = fetch_page(url, timeout=timeout, user_agent=user_agent)
    if page.text is not None:
        return page.text, "verbatim"
    return extract_markdown(page.content, base_url=page.url)


if __name__ == "__main__":
    sys.exit(main())
