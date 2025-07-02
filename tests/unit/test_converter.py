from unittest.mock import MagicMock

import pytest

from url2md4ai.converter import ContentExtractor


class TestContentExtractor:
    @pytest.fixture
    def extractor(self):
        return ContentExtractor()

    def test_is_valid_url(self, extractor):
        assert extractor._is_valid_url("https://example.com")
        assert extractor._is_valid_url("http://example.com")
        assert not extractor._is_valid_url("not_a_url")
        assert not extractor._is_valid_url("ftp://example.com")
        assert not extractor._is_valid_url("http://")  # Too short
        assert not extractor._is_valid_url("")  # Empty string

    def test_generate_filename(self, extractor):
        url = "https://example.com/page"
        filename = extractor.generate_filename(url)
        assert isinstance(filename, str)
        assert filename.endswith(".md")
        assert len(filename) == 19  # 16 chars hash + 3 chars extension

    @pytest.mark.asyncio
    async def test_extract_html_success(self, extractor, mocker):
        html_content = "<html><body><h1>Test</h1><p>Content</p></body></html>"
        mocker.patch.object(extractor, "_fetch_content", return_value=html_content)

        result = await extractor.extract_html("https://example.com")
        assert result == html_content

    @pytest.mark.asyncio
    async def test_extract_html_invalid_url(self, extractor):
        result = await extractor.extract_html("not_a_url")
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_html_fetch_failure(self, extractor, mocker):
        mocker.patch.object(extractor, "_fetch_content", return_value="")
        result = await extractor.extract_html("https://example.com")
        assert result == ""

    @pytest.mark.asyncio
    async def test_extract_markdown_with_html(self, extractor, mocker):
        html_content = "<html><body><h1>Test</h1><p>Content</p></body></html>"
        markdown_content = "# Test\\n\\nContent"
        mocker.patch("trafilatura.extract", return_value=markdown_content)

        result = await extractor.extract_markdown(
            "https://example.com",
            html_content=html_content,
            save_to_file=False,
        )

        assert result is not None
        assert result["markdown"] == markdown_content
        assert result["html_content"] == html_content
        assert "filename" in result

    @pytest.mark.asyncio
    async def test_extract_markdown_from_url(self, extractor, mocker):
        html_content = "<html><body><h1>Test</h1><p>Content</p></body></html>"
        markdown_content = "# Test\\n\\nContent"
        mocker.patch.object(extractor, "_fetch_content", return_value=html_content)
        mocker.patch("trafilatura.extract", return_value=markdown_content)

        result = await extractor.extract_markdown(
            "https://example.com",
            save_to_file=False,
        )
        assert result is not None
        assert result["markdown"] == markdown_content
        assert result["html_content"] == html_content

    @pytest.mark.asyncio
    async def test_extract_markdown_extraction_failure(self, extractor, mocker):
        html_content = "<html><body>Test</body></html>"
        mocker.patch("trafilatura.extract", return_value=None)
        result = await extractor.extract_markdown(
            "https://example.com",
            html_content=html_content,
            save_to_file=False,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_markdown_save_failure(self, extractor, mocker):
        html_content = "<html><body><h1>Test</h1></body></html>"
        markdown_content = "# Test"
        mocker.patch("trafilatura.extract", return_value=markdown_content)

        # Mock the config for output_dir
        extractor.config = MagicMock()
        extractor.config.output_dir = "/fake/dir"

        mocker.patch("pathlib.Path.write_text", side_effect=Exception("Save failed"))
        mocker.patch("pathlib.Path.mkdir", return_value=None)

        result = await extractor.extract_markdown(
            "https://example.com",
            html_content=html_content,
            save_to_file=True,
        )

        assert result is not None
        assert result["output_path"] == ""  # Should be empty on save failure
