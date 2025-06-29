# 🚀 url2md4ai

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![uv](https://img.shields.io/badge/dependency--manager-uv-orange.svg)
![Trafilatura](https://img.shields.io/badge/powered--by-trafilatura-brightgreen.svg)
![Playwright](https://img.shields.io/badge/js--rendering-playwright-orange.svg)

**🎯 Lean Python tool for extracting clean, LLM-optimized markdown from web pages**

Perfect for AI applications that need high-quality text extraction from both static and dynamic web content. Combines **Playwright** for JavaScript rendering with **Trafilatura** for intelligent content extraction, delivering markdown specifically optimized for LLM processing and information extraction.

## 🎯 Why url2md4ai?

**Traditional tools** extract everything: ads, cookie banners, navigation menus, social media widgets...  
**url2md4ai** extracts only what matters: clean, structured content ready for LLM processing.

```bash
# Example: Extract job posting from Satispay careers page
url2md4ai convert "https://www.satispay.com/careers/job-posting" --show-metadata

# Result: 97% noise reduction (from 51KB to 9KB)
# ✅ Clean job title, description, requirements, benefits
# ❌ No cookie banners, ads, or navigation clutter
```

**Perfect for:**
- 🤖 AI content analysis workflows
- 📊 LLM-based information extraction
- 🔍 Web scraping for research and analysis
- 📝 Content preprocessing for RAG systems
- 🎯 Automated content monitoring

## ✨ Features

### 🎯 **LLM-Optimized Text Extraction**
- **🧠 Smart Content Extraction**: Powered by Trafilatura for intelligent text extraction
- **🚀 Dynamic Content Support**: Full JavaScript rendering with Playwright for SPAs and dynamic sites
- **🧹 Clean Output**: Removes ads, cookie banners, navigation, and other noise for pure content
- **📊 Maximum Information Density**: Optimized markdown specifically designed for LLM processing

### ⚡ **Lean & Efficient**
- **🎯 Focused Purpose**: Built specifically for AI/LLM text extraction workflows
- **⚡ Fast Processing**: Optional non-JavaScript mode for static content (3x faster)
- **🔧 CLI-First**: Simple command-line interface for batch processing and automation
- **🐍 Python API**: Clean programmatic access for integration into AI pipelines

### 🛠️ **Production Ready**
- **📁 Smart Filenames**: Generate unique, deterministic filenames using URL hashes
- **🔄 Batch Processing**: Parallel processing support for multiple URLs
- **🎛️ Configurable**: Extensive configuration options for different content types
- **📈 Reliable**: Built-in retry logic and error handling

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
# Convert a single URL (with metadata)
url2md4ai convert "https://example.com" --show-metadata

# Convert with custom output file
url2md4ai convert "https://example.com" -o my_page.md

# Convert without JavaScript (3x faster for static content)
url2md4ai convert "https://example.com" --no-js

# Raw extraction (no LLM optimization)
url2md4ai convert "https://example.com" --raw
```

#### Batch Processing
```bash
# Convert multiple URLs with parallel processing
url2md4ai batch "https://site1.com" "https://site2.com" "https://site3.com" --concurrency 5

# Continue processing even if some URLs fail
url2md4ai batch "https://site1.com" "https://site2.com" --continue-on-error

# Custom output directory
url2md4ai batch "https://example.com" -d /path/to/output
```

#### Preview and Utilities
```bash
# Preview conversion without saving
url2md4ai preview "https://example.com" --show-content

# Test different extraction methods
url2md4ai test-extraction "https://example.com" --method both --show-diff

# Generate hash filename for URL
url2md4ai hash "https://example.com"

# Show current configuration
url2md4ai config-info --format json
```

### Python API

```python
from url2md4ai import URLToMarkdownConverter, Config

# Initialize converter
config = Config.from_env()
converter = URLToMarkdownConverter(config)

# Convert URL synchronously (perfect for LLM pipelines)
result = converter.convert_url_sync("https://example.com")

if result.success:
    print(f"📄 Title: {result.title}")
    print(f"📁 Saved as: {result.filename}")
    print(f"📊 Size: {result.file_size:,} characters")
    print(f"⚡ Method: {result.extraction_method}")
    print(f"⏱️  Processing time: {result.processing_time:.2f}s")
    
    # Use extracted content for LLM processing
    llm_ready_content = result.markdown
    print("🧠 LLM-ready content extracted successfully!")
else:
    print(f"❌ Error: {result.error}")

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

# Custom configuration for specific content types
config = Config(
    timeout=60,
    javascript_enabled=True,  # Essential for SPAs
    clean_content=True,       # Remove ads/banners
    llm_optimized=True,       # Optimize for LLM processing
    remove_cookie_banners=True,
    remove_navigation=True,
    remove_ads=True,
    output_dir="ai_content",
    user_agent="MyAI/1.0"
)

converter = URLToMarkdownConverter(config)

# Convert with maximum cleaning for LLM processing
result = await converter.convert_url(
    url="https://example.com",
    use_javascript=True,      # Handle dynamic content
    use_trafilatura=True      # Use intelligent extraction
)

if result.success:
    # Perfect for feeding into LLMs
    clean_content = result.markdown
    metadata = result.metadata
    
    print(f"🎯 Extraction quality: {result.extraction_method}")
    print(f"📊 Content size: {result.file_size:,} chars")
    print(f"🧹 Cleaned and ready for LLM processing!")

# Generate deterministic filenames
hash_value = URLHasher.generate_hash("https://example.com")
filename = URLHasher.generate_filename("https://example.com")
print(f"🔑 Hash: {hash_value}, 📁 Filename: {filename}")
```

## 📊 Extraction Quality Examples

### Before vs After: Real-World Results

```bash
# Complex job posting with cookie banners and ads
url2md4ai convert "https://company.com/careers/position" --show-metadata
```

**Before (Raw HTML):** 51KB, 797 lines
- ❌ Cookie consent banners
- ❌ Website navigation
- ❌ Social media widgets  
- ❌ Advertising content
- ❌ Footer links and legal text

**After (url2md4ai):** 9KB, 69 lines
- ✅ Job title and description
- ✅ Key requirements
- ✅ Company benefits
- ✅ Application process
- ✅ **97% noise reduction!**

### Content Types Optimized for LLM

| Content Type | Extraction Quality | Best Settings |
|--------------|-------------------|---------------|
| **News Articles** | ⭐⭐⭐⭐⭐ | `--no-js` (faster) |
| **Job Postings** | ⭐⭐⭐⭐⭐ | `--force-js` (complete) |
| **Product Pages** | ⭐⭐⭐⭐ | `--clean` (essential) |
| **Documentation** | ⭐⭐⭐⭐⭐ | `--raw` (preserve structure) |
| **Blog Posts** | ⭐⭐⭐⭐⭐ | default settings |
| **Social Media** | ⭐⭐⭐ | `--force-js` required |

## ⚙️ Configuration

### Environment Variables

```bash
# LLM-Optimized Extraction Settings
export URL2MD_CLEAN_CONTENT=true
export URL2MD_LLM_OPTIMIZED=true
export URL2MD_USE_TRAFILATURA=true

# Content Filtering (Noise Removal)
export URL2MD_REMOVE_COOKIES=true
export URL2MD_REMOVE_NAV=true
export URL2MD_REMOVE_ADS=true
export URL2MD_REMOVE_SOCIAL=true

# JavaScript Rendering
export URL2MD_JAVASCRIPT=true
export URL2MD_HEADLESS=true
export URL2MD_PAGE_TIMEOUT=2000

# Output Settings
export URL2MD_OUTPUT_DIR="output"
export URL2MD_USE_HASH_FILENAMES=true

# Performance & Reliability
export URL2MD_TIMEOUT=30
export URL2MD_MAX_RETRIES=3
export URL2MD_USER_AGENT="url2md4ai/1.0"
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| **LLM Optimization** | | |
| `clean_content` | true | Remove ads, banners, navigation |
| `llm_optimized` | true | Post-process for LLM consumption |
| `use_trafilatura` | true | Use intelligent text extraction |
| **Content Filtering** | | |
| `remove_cookie_banners` | true | Remove cookie consent UI |
| `remove_navigation` | true | Remove nav menus and headers |
| `remove_ads` | true | Remove advertising content |
| `remove_social_media` | true | Remove social sharing widgets |
| **JavaScript Rendering** | | |
| `javascript_enabled` | true | Enable dynamic content rendering |
| `browser_headless` | true | Run browser in headless mode |
| `page_wait_timeout` | 2000 | Wait time for page loading (ms) |
| **Output Settings** | | |
| `output_dir` | "output" | Default output directory |
| `use_hash_filenames` | true | Generate deterministic filenames |

## 🐳 Docker Usage

📖 **See [DOCKER_USAGE.md](DOCKER_USAGE.md) for comprehensive Docker usage examples and troubleshooting.**

### Quick Start with Docker

```bash
# Build the image
docker build -t url2md4ai .

# Convert single URL with LLM optimization
docker run --rm \
  -v $(pwd)/output:/app/output \
  url2md4ai \
  convert "https://example.com" --show-metadata

# Convert dynamic content with JavaScript rendering
docker run --rm \
  -v $(pwd)/output:/app/output \
  url2md4ai \
  convert "https://spa-app.com" --force-js --show-metadata

# Batch processing with parallel workers
docker run --rm \
  -v $(pwd)/output:/app/output \
  url2md4ai \
  batch "https://site1.com" "https://site2.com" --concurrency 5 --show-metadata
```

### Using Docker Compose (Recommended)

```bash
# Start with compose for easier management
docker compose run --rm url2md4ai convert "https://example.com" --show-metadata

# Development mode with full environment
docker compose run --rm dev

# Batch processing example
docker compose run --rm url2md4ai \
  batch "https://news.site.com/article1" "https://blog.site.com/post2" \
  --concurrency 3 --continue-on-error --show-metadata
```

### Custom Configuration

```bash
# Override LLM optimization settings
docker run --rm \
  -v $(pwd)/output:/app/output \
  -e URL2MD_CLEAN_CONTENT=false \
  -e URL2MD_LLM_OPTIMIZED=false \
  url2md4ai \
  convert "https://example.com" --raw

# Disable JavaScript for faster processing
docker run --rm \
  -v $(pwd)/output:/app/output \
  -e URL2MD_JAVASCRIPT=false \
  url2md4ai \
  convert "https://static-site.com" --no-js
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

- [Trafilatura](https://trafilatura.readthedocs.io/) for intelligent content extraction and web scraping
- [Playwright](https://playwright.dev/) for JavaScript rendering and dynamic content handling
- [html2text](https://github.com/Alir3z4/html2text) for HTML to Markdown conversion
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing and content cleaning
- [Click](https://click.palletsprojects.com/) for the powerful CLI interface
- [Loguru](https://github.com/Delgan/loguru) for elegant logging

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
