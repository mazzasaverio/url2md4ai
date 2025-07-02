"""Rate limiting and caching utilities."""

import hashlib
import threading
import time
from collections import deque
from typing import Any, cast

from .logger import get_logger


class RateLimiter:
    """Simple rate limiter using sliding window."""

    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute allowed
        """
        self.requests_per_minute = requests_per_minute
        self.requests: deque[float] = deque()
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)

    def acquire(self) -> bool:
        """Try to acquire a slot for making a request.

        Returns:
            True if request can be made, False if rate limited
        """
        with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            while self.requests and self.requests[0] < now - 60:
                self.requests.popleft()

            if len(self.requests) >= self.requests_per_minute:
                self.logger.warning(
                    f"Rate limit exceeded: {len(self.requests)}/{self.requests_per_minute} RPM",
                )
                return False

            self.requests.append(now)
            return True

    def wait_if_needed(self) -> None:
        """Wait until a request slot becomes available."""
        while not self.acquire():
            # Wait until the oldest request expires
            if self.requests:
                sleep_time = 60 - (time.time() - self.requests[0]) + 0.1
                if sleep_time > 0:
                    self.logger.info(f"Rate limited, waiting {sleep_time:.1f} seconds")
                    time.sleep(sleep_time)


class SimpleCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache.

        Args:
            ttl_seconds: Time to live for cache entries in seconds
        """
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, tuple[Any, float]] = {}
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)

    def _generate_key(
        self,
        text: str,
        schema_name: str,
        model: str,
        temperature: float,
    ) -> str:
        """Generate cache key from extraction parameters."""
        content = f"{text}:{schema_name}:{model}:{temperature}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _generate_url_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.sha256(url.encode()).hexdigest()

    def get(
        self,
        text: str,
        schema_name: str,
        model: str,
        temperature: float,
    ) -> dict[str, Any] | None:
        """Get cached result if available and not expired.

        Args:
            text: Input text
            schema_name: Schema identifier
            model: OpenAI model name
            temperature: Model temperature

        Returns:
            Cached result or None if not found/expired
        """
        key = self._generate_key(text, schema_name, model, temperature)

        with self.lock:
            if key in self.cache:
                result, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    self.logger.debug(f"Cache hit for key: {key[:16]}...")
                    return cast("dict[str, Any]", result)
                # Expired, remove it
                del self.cache[key]
                self.logger.debug(f"Cache expired for key: {key[:16]}...")

        return None

    def set(
        self,
        text: str,
        schema_name: str,
        model: str,
        temperature: float,
        result: dict[str, Any],
    ) -> None:
        """Store result in cache.

        Args:
            text: Input text
            schema_name: Schema identifier
            model: OpenAI model name
            temperature: Model temperature
            result: Result to cache
        """
        key = self._generate_key(text, schema_name, model, temperature)

        with self.lock:
            self.cache[key] = (result, time.time())
            self.logger.debug(f"Cached result for key: {key[:16]}...")

    def clear_expired(self) -> int:
        """Clear expired entries from cache.

        Returns:
            Number of entries cleared
        """
        now = time.time()
        expired_keys = []

        with self.lock:
            for key, (_, timestamp) in self.cache.items():
                if now - timestamp >= self.ttl_seconds:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

        if expired_keys:
            self.logger.info(f"Cleared {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def clear_all(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            if count > 0:
                self.logger.info(f"Cleared all {count} cache entries")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            now = time.time()
            total_entries = len(self.cache)
            expired_entries = sum(
                1
                for _, timestamp in self.cache.values()
                if now - timestamp >= self.ttl_seconds
            )

            return {
                "total_entries": total_entries,
                "active_entries": total_entries - expired_entries,
                "expired_entries": expired_entries,
                "ttl_seconds": self.ttl_seconds,
            }
