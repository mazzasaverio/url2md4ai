"""Pure-text post-processing: whitespace, optional link stripping, frontmatter."""

import datetime
import re

# [text](url) but not ![alt](src): images carry information, link URLs often don't.
_LINK_RE = re.compile(r"(?<!\!)\[([^\]]+)\]\([^)]*\)")
_TRAILING_WS_RE = re.compile(r"[ \t]+$", flags=re.MULTILINE)
_EXTRA_NEWLINES_RE = re.compile(r"\n{3,}")


def strip_links(markdown: str) -> str:
    """Replace ``[text](url)`` with ``text``, preserving images."""
    return _LINK_RE.sub(r"\1", markdown)


def normalize_whitespace(markdown: str) -> str:
    """Trim trailing spaces, collapse 3+ blank lines, ensure one final newline."""
    markdown = _TRAILING_WS_RE.sub("", markdown)
    markdown = _EXTRA_NEWLINES_RE.sub("\n\n", markdown)
    return markdown.strip() + "\n"


def build_frontmatter(*, title: str | None, source: str, fetched: datetime.date) -> str:
    """YAML frontmatter with the three fixed keys; title omitted when unknown."""
    lines = ["---"]
    if title:
        escaped = title.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'title: "{escaped}"')
    lines.append(f"source: {source}")
    lines.append(f"fetched: {fetched.isoformat()}")
    lines.append("---\n")
    return "\n".join(lines)
