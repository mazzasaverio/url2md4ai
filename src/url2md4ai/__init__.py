"""
url2md4ai: Convert web pages to LLM-optimized markdown from URLs.

A powerful Python library for converting web pages to clean, LLM-optimized markdown.
Supports dynamic content rendering with JavaScript and generates unique filenames
based on URL hashes.
"""

__version__ = "0.0.3"

from .config import Config
from .converter import ConversionResult, URLHasher, URLToMarkdownConverter
from .utils import (
    get_logger,
    setup_logger,
)

__all__ = [
    "Config",
    "ConversionResult",
    "URLHasher",
    "URLToMarkdownConverter",
    "get_logger",
    "setup_logger",
]
