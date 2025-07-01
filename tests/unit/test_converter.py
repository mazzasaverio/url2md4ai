import pytest

from url2md4ai.config import Config
from url2md4ai.converter import (
    ContentCleaner,
    ConversionResult,
    URLHasher,
    URLToMarkdownConverter,
)


class TestURLHasher:
    def test_generate_filename(self):
        url = "https://example.com/page"
        hasher = URLHasher()
        filename = hasher.generate_filename(url)
        assert isinstance(filename, str)
        assert filename.endswith(".md")
        assert len(filename) == 19  # 16 chars hash + 3 chars extension

    def test_generate_hash(self):
        url = "https://example.com/page"
        hasher = URLHasher()
        hash_value = hasher.generate_hash(url)
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16


class TestContentCleaner:
    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def cleaner(self, config):
        return ContentCleaner(config)

    def test_clean_with_trafilatura(self, cleaner):
        html_content = """
        <html>
            <body>
                <h1>Test Title</h1>
                <p>Test content</p>
            </body>
        </html>
        """
        result = cleaner.clean_with_trafilatura(html_content, "https://example.com")
        assert result is not None
        assert "Test Title" in result
        assert "Test content" in result

    def test_clean_with_trafilatura_failure(self, cleaner):
        # Test with invalid HTML
        result = cleaner.clean_with_trafilatura("<invalid>", "https://example.com")
        assert result is None

        # Test with empty content
        result = cleaner.clean_with_trafilatura("", "https://example.com")
        assert result is None


class TestConversionResult:
    def test_success_result(self):
        result = ConversionResult.success_result(
            url="https://example.com",
            markdown="# Test",
            title="Test Page",
        )
        assert result.success is True
        assert result.url == "https://example.com"
        assert result.markdown == "# Test"
        assert result.title == "Test Page"
        assert not result.error

    def test_error_result(self):
        result = ConversionResult.error_result(
            error="Failed to fetch",
            url="https://example.com",
        )
        assert result.success is False
        assert result.url == "https://example.com"
        assert result.error == "Failed to fetch"
        assert not result.markdown


class TestURLToMarkdownConverter:
    @pytest.fixture
    def converter(self):
        return URLToMarkdownConverter()

    def test_is_valid_url(self, converter):
        assert converter._is_valid_url("https://example.com")
        assert converter._is_valid_url("http://example.com")
        assert not converter._is_valid_url("not_a_url")
        assert not converter._is_valid_url("ftp://example.com")

    @pytest.mark.asyncio
    async def test_convert_url_invalid_url(self, converter):
        result = await converter.convert_url("not_a_url")
        assert not result.success
        assert "Invalid URL" in result.error
