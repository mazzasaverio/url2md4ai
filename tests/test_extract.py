"""Extraction: main content in, boilerplate out, graceful failure."""

import pytest
from conftest import load_fixture

from url2md4ai import ExtractionError
from url2md4ai._extract import extract_markdown, extract_title


def test_article_keeps_content_drops_chrome():
    markdown, strategy = extract_markdown(load_fixture("article.html"))
    assert "Idempotency first" in markdown
    assert "store.upsert" in markdown  # code block survives
    assert "Sign in" not in markdown  # nav dropped
    assert "newsletter" not in markdown  # footer dropped
    assert strategy in {"primary", "recall-retry", "baseline"}


def test_js_only_page_raises():
    with pytest.raises(ExtractionError, match="JavaScript"):
        extract_markdown(load_fixture("js_only.html"))


def test_spa_with_jsonld_falls_back_to_structured_data():
    markdown, strategy = extract_markdown(load_fixture("jsonld_spa.html"))
    assert strategy == "jsonld"
    assert "# Backend Engineer" in markdown
    assert "ingestion services" in markdown
    assert "<h2>" not in markdown  # HTML in the description is converted


def test_title_extraction():
    assert extract_title(load_fixture("article.html")) == "Designing Resilient Data Pipelines"
