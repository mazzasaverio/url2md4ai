"""Utility functions and classes for url2md4ai."""

from typing import TYPE_CHECKING

from .logger import get_logger, setup_logger
from .rate_limiter import RateLimiter

if TYPE_CHECKING:
    from ..converter import URLHasher


# URLHasher is imported from converter to avoid circular imports
def url_hasher() -> type["URLHasher"]:
    """URLHasher is available in converter module."""
    from ..converter import URLHasher as _URLHasher

    return _URLHasher


__all__ = [
    "RateLimiter",
    "get_logger",
    "setup_logger",
    "url_hasher",
]
