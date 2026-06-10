"""Pure post-processing functions."""

import datetime

from url2md4ai._postprocess import build_frontmatter, normalize_whitespace, strip_links


def test_strip_links_keeps_text():
    assert strip_links("see [the docs](https://x.example) now") == "see the docs now"


def test_strip_links_preserves_images():
    md = "![a lake](img.jpg) and [a link](https://x.example)"
    assert strip_links(md) == "![a lake](img.jpg) and a link"


def test_normalize_whitespace():
    assert normalize_whitespace("a  \n\n\n\nb\n") == "a\n\nb\n"


def test_frontmatter_with_title():
    fm = build_frontmatter(
        title='The "Best" Guide', source="https://x.example", fetched=datetime.date(2026, 6, 10)
    )
    assert fm == (
        '---\ntitle: "The \\"Best\\" Guide"\nsource: https://x.example\nfetched: 2026-06-10\n---\n'
    )


def test_frontmatter_without_title():
    fm = build_frontmatter(
        title=None, source="https://x.example", fetched=datetime.date(2026, 6, 10)
    )
    assert "title" not in fm
    assert "source: https://x.example" in fm
