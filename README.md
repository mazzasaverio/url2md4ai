# 🚀 url2md4ai

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![uv](https://img.shields.io/badge/dependency--manager-uv-orange.svg)
![Trafilatura](https://img.shields.io/badge/powered--by-trafilatura-brightgreen.svg)
![Playwright](https://img.shields.io/badge/js--rendering-playwright-orange.svg)

**🎯 A lean Python tool for extracting clean, LLM-optimized markdown from web pages.**

Perfect for AI applications that need high-quality text extraction from both static and dynamic web content. It combines **Playwright** for JavaScript rendering with **Trafilatura** for intelligent content extraction, delivering clean markdown ready for LLM processing.

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

- **🧠 Smart Content Extraction**: Powered by `trafilatura` for intelligent text extraction from HTML.
- **🚀 Dynamic Content Support**: Uses `playwright` to render JavaScript on web pages, ensuring content from SPAs and dynamic sites is captured.
- **🧹 Clean Output**: Removes ads, cookie banners, navigation, and other noise for a cleaner final output.
- **🐍 Simple API**: A straightforward Python API and CLI for easy integration into your workflows.
- **📁 Deterministic Filenames**: Generates unique, hash-based filenames from URLs for consistent output.

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

### Using `uv` (Recommended)

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

### Using `pip`

```bash
pip install url2md4ai
playwright install chromium
url2md4ai convert "https://example.com"
```

### Using Docker

See [DOCKER_USAGE.md](DOCKER_USAGE.md) for instructions on how to use the provided Docker setup.

## 📖 Usage

### Command-Line Interface (CLI)

The CLI provides a simple way to convert URLs to markdown or extract raw HTML.

#### Convert a URL to Markdown

```bash
# Convert a single URL and print to console
url2md4ai convert "https://example.com" --no-save

# Save the markdown to the default 'output' directory
url2md4ai convert "https://example.com"

# Specify a custom output directory
url2md4ai convert "https://example.com" --output-dir my_markdown
```

#### Extract Raw HTML from a URL

```bash
# Get the raw HTML of a page and print it to the console
url2md4ai extract-html "https://example.com"
```

#### Convert a Local HTML File

```bash
# Convert a local HTML file to markdown
url2md4ai convert-html my_page.html
```

For more options, use the `--help` flag with any command:
```bash
url2md4ai convert --help
```

### Python API

The Python API provides programmatic access to the content extraction functionality.

```python
import asyncio
from url2md4ai import ContentExtractor

# Initialize the extractor
extractor = ContentExtractor()

async def main():
    url = "https://example.com"

    # Extract clean markdown from a URL
    markdown_result = await extractor.extract_markdown(url)
    if markdown_result:
        print("--- MARKDOWN ---")
        print(markdown_result["markdown"])
        print(f"\\nSaved to: {markdown_result['output_path']}")

    # Extract raw HTML from a URL
    html_content = await extractor.extract_html(url)
    if html_content:
        print("\\n--- HTML ---")
        print(html_content[:200] + "...")  # Print first 200 characters

asyncio.run(main())
```

#### Synchronous Usage

For use cases where you can't use `asyncio`, synchronous wrappers are available:

```python
from url2md4ai import ContentExtractor

extractor = ContentExtractor()
url = "https://example.com"

# Synchronously extract markdown
markdown_result = extractor.extract_markdown_sync(url)
if markdown_result:
    print(markdown_result["markdown"])

# Synchronously extract HTML
html_content = extractor.extract_html_sync(url)
if html_content:
    print(html_content[:200] + "...")
```

## 🛠️ Configuration

The behavior of the `ContentExtractor` can be customized through a `Config` object or environment variables.

**Example: Custom Configuration**

```python
from url2md4ai import ContentExtractor, Config

# Customize configuration
config = Config(
    timeout=60,                  # Page load timeout in seconds
    user_agent="MyTestAgent/1.0", # Custom User-Agent
    output_dir="custom_output",  # Default output directory
    browser_headless=True,       # Run Playwright in headless mode
    wait_for_network_idle=True,  # Wait for network to be idle
    page_wait_timeout=2000       # Additional wait time in ms
)

extractor = ContentExtractor(config=config)

# This will use the custom configuration
extractor.extract_markdown_sync("https://example.com")
```

See `src/url2md4ai/config.py` for all available configuration options and their corresponding environment variables.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

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
