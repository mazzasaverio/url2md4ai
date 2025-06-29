# 🌐 url2md4ai

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![uv](https://img.shields.io/badge/dependency--manager-uv-orange.svg)

A powerful Python library and CLI tool for converting web pages to clean, LLM-optimized markdown from URLs. Supports dynamic content rendering with JavaScript and generates unique filenames based on URL hashes.

## ✨ Features

- **🎯 URL to Markdown**: Convert any web page to clean, LLM-ready markdown
- **🚀 JavaScript Rendering**: Full support for dynamic content with Playwright
- **📁 Smart Filenames**: Generate unique filenames using URL hashes
- **🔧 CLI Interface**: Easy-to-use command-line tool for batch processing
- **🐍 Python API**: Programmatic access for integration into your applications
- **⚡ Fast Mode**: Optional non-JavaScript mode for faster processing
- **🧹 Clean Output**: Optimized markdown formatting for LLM processing
- **📊 Batch Processing**: Convert multiple URLs with parallel processing support

## 🚀 Quick Start

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/mazzasaverio/url2md4ai.git
cd url2md4ai
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Convert your first URL
uv run url2md4ai convert "https://example.com"
```

### Using pip

```bash
pip install url2md4ai
playwright install chromium
url2md4ai convert "https://example.com"
```

### Using Docker

```bash
# Build the image
docker build -t url2md4ai .

# Run with URL conversion
docker run --rm \
  -v $(pwd)/output:/app/output \
  url2md4ai \
  convert "https://example.com"
```

## 📖 Usage

### CLI Commands

#### Basic Conversion
```bash
# Convert a single URL
url2md4ai convert "https://example.com"

# Convert with custom output file
url2md4ai convert "https://example.com" -o my_page.md

# Convert without JavaScript (faster, but may miss dynamic content)
url2md4ai convert "https://example.com" --no-javascript
```

#### Batch Processing
```bash
# Convert multiple URLs
url2md4ai batch "https://site1.com" "https://site2.com" "https://site3.com"

# Parallel processing (faster)
url2md4ai batch "https://site1.com" "https://site2.com" --parallel

# Custom output directory
url2md4ai batch "https://example.com" -d /path/to/output
```

#### Preview and Utilities
```bash
# Preview conversion without saving
url2md4ai preview "https://example.com"

# Generate hash filename for URL
url2md4ai hash "https://example.com"

# Show current configuration
url2md4ai config-info
```

### Python API

```python
from url2md4ai import URLToMarkdownConverter, Config

# Initialize converter
config = Config.from_env()
converter = URLToMarkdownConverter(config)

# Convert URL synchronously
result = converter.convert_url_sync("https://example.com")

if result.success:
    print(f"Title: {result.metadata['title']}")
    print(f"Filename: {result.filename}")
    print("Markdown content:")
    print(result.markdown)
else:
    print(f"Error: {result.error}")

# Convert URL asynchronously
import asyncio

async def convert_url():
    result = await converter.convert_url("https://example.com")
    return result

result = asyncio.run(convert_url())
```

#### Advanced Usage

```python
from url2md4ai import URLToMarkdownConverter, Config, URLHasher

# Custom configuration
config = Config(
    timeout_seconds=60,
    headless=False,  # Show browser window
    javascript_enabled=True,
    output_dir="custom_output",
    user_agent="MyBot/1.0"
)

converter = URLToMarkdownConverter(config)

# Convert with custom settings
result = converter.convert_url_sync(
    url="https://example.com",
    output_path="custom_filename.md",
    use_javascript=True
)

# Generate URL hash
hash_value = URLHasher.hash_url("https://example.com")
filename = URLHasher.create_filename("https://example.com", use_hash=True)
print(f"Hash: {hash_value}, Filename: {filename}")
```

## ⚙️ Configuration

### Environment Variables

```bash
# Web scraping settings
export URL2MD_TIMEOUT_SECONDS=30
export URL2MD_USER_AGENT="url2md4ai/1.0"
export URL2MD_MAX_RETRIES=3

# Playwright settings
export URL2MD_HEADLESS=true
export URL2MD_JAVASCRIPT_ENABLED=true
export URL2MD_WAIT_NETWORK_IDLE=true

# Output settings
export URL2MD_OUTPUT_DIR="output"
export URL2MD_USE_HASH_FILENAME=true

# Performance settings
export URL2MD_ENABLE_CACHING=true
export URL2MD_CACHE_TTL_SECONDS=3600

# Logging
export URL2MD_LOG_LEVEL=INFO
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `timeout_seconds` | 30 | Request timeout in seconds |
| `user_agent` | `url2md4ai/1.0` | User-Agent string for requests |
| `max_retries` | 3 | Maximum retry attempts |
| `headless` | true | Run browser in headless mode |
| `javascript_enabled` | true | Enable JavaScript rendering |
| `wait_for_network_idle` | true | Wait for network idle before extraction |
| `output_dir` | "output" | Default output directory |
| `use_url_hash_filename` | true | Use URL hash for filenames |
| `enable_caching` | true | Enable result caching |

## 🐳 Docker Usage

### Development with Docker

```bash
# Build development image
docker build -t url2md4ai:dev .

# Run interactive shell
docker run -it --rm \
  -v $(pwd):/app \
  url2md4ai:dev \
  /bin/bash

# Convert URL with mounted output
docker run --rm \
  -v $(pwd)/output:/app/output \
  url2md4ai:dev \
  convert "https://example.com"
```

### Production Deployment

```bash
# Production container with batch processing
docker run -d \
  --name url2md4ai-service \
  -v /path/to/output:/app/output \
  -e URL2MD_OUTPUT_DIR=/app/output \
  url2md4ai:latest

# Process URLs via mounted volume or API calls
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/mazzasaverio/url2md4ai.git
cd url2md4ai

# Install with uv
uv sync

# Install Playwright browsers
uv run playwright install

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run black --check .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/url2md4ai

# Run specific test
uv run pytest tests/test_converter.py
```

## 📊 Output Format

The tool generates clean, LLM-optimized markdown with:

- ✅ Preserved heading structure
- ✅ Clean link formatting
- ✅ Removed navigation, footer, and sidebar content
- ✅ Optimized whitespace and line breaks
- ✅ Title and metadata preservation
- ✅ Support for complex layouts

### Example Output

```markdown
# Page Title

Main content paragraph with [links](https://example.com) preserved.

## Section Heading

- List items preserved
- Proper formatting maintained

**Bold text** and *italic text* converted correctly.

> Blockquotes maintained

```code blocks preserved```
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality

- Use `black` for code formatting
- Use `ruff` for linting
- Add type hints for all functions
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for JavaScript rendering
- [html2text](https://github.com/Alir3z4/html2text) for HTML to Markdown conversion
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Click](https://click.palletsprojects.com/) for CLI interface

## 📈 Roadmap

- [ ] Support for more output formats (PDF, DOCX)
- [ ] Custom CSS selector filtering
- [ ] Integration with popular LLM APIs
- [ ] Web UI interface
- [ ] Plugin system for custom processors
- [ ] Support for authentication-required pages

---

<div align="center">
  <strong>Made with ❤️ by <a href="https://github.com/mazzasaverio">Saverio Mazza</a></strong>
</div>
