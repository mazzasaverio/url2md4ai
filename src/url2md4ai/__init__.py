"""
url2md4ai: Convert web pages to LLM-optimized markdown from URLs.

A powerful Python library for converting web pages to clean, LLM-optimized markdown.
Supports dynamic content rendering with JavaScript and generates unique filenames
based on URL hashes.
"""

__version__ = "0.1.1"

from url2md4ai.config import Config
from url2md4ai.converter import (
    ContentExtractor,
)

from .utils import (
    get_logger,
    setup_logger,
)

__all__ = [
    "Config",
    "ContentExtractor",
    "get_logger",
    "setup_logger",
]
