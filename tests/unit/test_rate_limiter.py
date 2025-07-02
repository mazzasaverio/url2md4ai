import time

import pytest

from url2md4ai.utils.rate_limiter import RateLimiter, SimpleCache


class TestSimpleCache:
    @pytest.fixture
    def cache(self):
        return SimpleCache(ttl_seconds=1)

    def test_get_and_set(self, cache):
        # Test extraction cache
        text = "test text"
        schema_name = "test_schema"
        model = "gpt-4"
        temperature = 0.7
        result = {"key": "value"}

        # Initially should be None
        assert cache.get(text, schema_name, model, temperature) is None

        # Set and get
        cache.set(text, schema_name, model, temperature, result)
        cached = cache.get(text, schema_name, model, temperature)
        assert cached == result

    def test_cache_expiration(self, cache):
        text = "test text"
        schema_name = "test_schema"
        model = "gpt-4"
        temperature = 0.7
        result = {"key": "value"}

        cache.set(text, schema_name, model, temperature, result)
        assert cache.get(text, schema_name, model, temperature) == result

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get(text, schema_name, model, temperature) is None

    def test_clear_expired(self, cache):
        # Add some entries
        cache.set("text1", "schema1", "model1", 0.7, {"key": "value1"})
        cache.set("text2", "schema2", "model2", 0.7, {"key": "value2"})

        # Wait for expiration
        time.sleep(1.1)

        # Clear expired entries
        cleared = cache.clear_expired()
        assert cleared == 2

        # Cache should be empty
        assert cache.get("text1", "schema1", "model1", 0.7) is None
        assert cache.get("text2", "schema2", "model2", 0.7) is None

    def test_clear_all(self, cache):
        # Add some entries
        cache.set("text1", "schema1", "model1", 0.7, {"key": "value1"})
        cache.set("text2", "schema2", "model2", 0.7, {"key": "value2"})

        # Clear all entries
        cache.clear_all()

        # Cache should be empty
        assert cache.get("text1", "schema1", "model1", 0.7) is None
        assert cache.get("text2", "schema2", "model2", 0.7) is None

    def test_get_stats(self, cache):
        # Add some entries
        cache.set("text1", "schema1", "model1", 0.7, {"key": "value1"})
        cache.set("text2", "schema2", "model2", 0.7, {"key": "value2"})

        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2
        assert stats["expired_entries"] == 0
        assert stats["ttl_seconds"] == 1


class TestRateLimiter:
    @pytest.fixture
    def rate_limiter(self):
        return RateLimiter(requests_per_minute=60)

    def test_acquire_within_limit(self, rate_limiter):
        # Should be able to acquire when under limit
        assert rate_limiter.acquire() is True

    @pytest.mark.usefixtures("rate_limiter")
    def test_rate_limiting(self):
        # Set a very low limit for testing
        limiter = RateLimiter(requests_per_minute=2)

        # First two requests should succeed
        assert limiter.acquire() is True
        assert limiter.acquire() is True

        # Third request should fail
        assert limiter.acquire() is False
