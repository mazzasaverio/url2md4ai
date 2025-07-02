# Docker Usage Guide

This guide shows how to use Docker with the **url2md4ai** project for converting web pages to clean, LLM-ready markdown.

## 🚀 Quick Start

The simplest way to use the Docker image is to build it and run the `convert` command.

```bash
# 1. Build the Docker image
docker build -t url2md4ai .

# 2. Run the conversion
# This command mounts the local 'output' directory into the container
# and saves the generated markdown file there.
docker run --rm \\
    -v "$(pwd)/output:/app/output" \\
    url2md4ai \\
    convert "https://example.com"
```

The converted file will appear in the `output` directory on your host machine.

## ⚙️ Docker Compose

For a more streamlined experience, you can use the provided `docker-compose.yml`.

### Basic Conversion

```bash
# Convert a single URL and save to the output directory
docker compose run --rm url2md4ai convert "https://example.com"

# Convert and print to console instead of saving
docker compose run --rm url2md4ai convert "https://example.com" --no-save
```

### Extracting HTML

```bash
# Extract the raw HTML of a page and print to the console
docker compose run --rm url2md4ai extract-html "https://example.com"
```

### Development Environment

The `dev` service in the `docker-compose.yml` file provides an interactive shell within the container, with your local source code mounted. This is useful for development and running tests.

```bash
# Start an interactive development environment
docker compose run --rm dev

# Inside the container, you can run commands like:
uv run pytest
uv run ruff check .
uv run url2md4ai convert "https://example.com"
```

## 🛠️ Available Commands

The Docker entrypoint is set to `url2md4ai`, so you can run any of the CLI commands.

### `convert`

Converts a URL to markdown.

```bash
docker compose run --rm url2md4ai convert [OPTIONS] <URL>
```

**Common Options:**
- `--output-dir <DIR>`: Directory to save the markdown file.
- `--no-save`: Print the markdown to the console instead of saving to a file.
- `--json`: Output the result as a JSON object.

### `extract-html`

Extracts the raw HTML from a URL.

```bash
docker compose run --rm url2md4ai extract-html [OPTIONS] <URL>
```

### `convert-html`

Converts a local HTML file to markdown. You'll need to mount the file into the container.

```bash
# Assuming 'my_page.html' is in your current directory
docker run --rm \\
    -v "$(pwd)/my_page.html:/app/my_page.html" \\
    -v "$(pwd)/output:/app/output" \\
    url2md4ai \\
    convert-html /app/my_page.html
```

## 📦 Volume Mounts

The Docker setup uses a volume mount to persist the output files:
- `./output` → `/app/output`

This means any files saved to `/app/output` inside the container will be available in the `output` directory on your host machine.

## Docker Setup Options

### 1. Using Docker Compose (Recommended)

**Production service:**
```bash
# Build and show help
docker compose up url2md4ai

# Convert single URL
docker compose run --rm url2md4ai convert "https://example.com" --show-metadata

# Convert without JavaScript (faster for static content)
docker compose run --rm url2md4ai convert "https://example.com" --no-js

# Batch processing
docker compose run --rm url2md4ai batch "https://site1.com" "https://site2.com" --concurrency 3

# Preview without saving
docker compose run --rm url2md4ai preview "https://example.com" --show-content

# Test extraction methods
docker compose run --rm url2md4ai test-extraction "https://example.com" --method both --show-diff
```

**Development service:**
```bash
# Start interactive development environment
docker compose run --rm dev

# Inside the container you can run:
uv run url2md4ai convert "https://example.com"
uv run pytest
uv run ruff check .
```

### 2. Using Helper Scripts

**For Development:**
```bash
./scripts/docker-dev.sh
```

**For Production Use:**
```bash
# Show help
./scripts/docker-run.sh

# Convert single URL
./scripts/docker-run.sh convert "https://example.com" --show-metadata

# Batch processing
./scripts/docker-run.sh batch "https://site1.com" "https://site2.com" --concurrency 5

# Preview mode
./scripts/docker-run.sh preview "https://example.com" --show-content

# Generate hash for URL
./scripts/docker-run.sh hash "https://example.com"

# Show configuration
./scripts/docker-run.sh config-info --format json
```

### 3. Direct Docker Commands

**Build the image:**
```bash
docker build -t url2md4ai:latest .
```

**Run commands:**
```bash
# Convert single URL
docker run --rm \
    -v "$(pwd)/output:/app/output" \
    url2md4ai:latest \
    convert "https://example.com" --show-metadata

# Batch processing
docker run --rm \
    -v "$(pwd)/output:/app/output" \
    url2md4ai:latest \
    batch "https://site1.com" "https://site2.com" "https://site3.com" --concurrency 5

# Preview without saving
docker run --rm \
    url2md4ai:latest \
    preview "https://example.com" --show-content

# Test extraction methods
docker run --rm \
    url2md4ai:latest \
    test-extraction "https://example.com" --method both --show-diff
```

## Environment Variables

Configure url2md4ai behavior with environment variables:

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

# Performance & Reliability
export URL2MD_TIMEOUT=30
export URL2MD_MAX_RETRIES=3
export URL2MD_USER_AGENT="url2md4ai-docker/1.0"
export URL2MD_LOG_LEVEL=INFO
```

## Complete Examples

### Convert News Article (Static Content)
```bash
# Fast conversion without JavaScript
docker compose run --rm url2md4ai \
    convert "https://news.example.com/article" --no-js --show-metadata
```

### Convert Job Posting (Dynamic Content)
```bash
# Full JavaScript rendering for complete extraction
docker compose run --rm url2md4ai \
    convert "https://company.com/careers/position" --force-js --show-metadata
```

### Batch Processing for Research
```bash
# Convert multiple URLs with parallel processing
docker compose run --rm url2md4ai \
    batch \
    "https://site1.com/page1" \
    "https://site2.com/page2" \
    "https://site3.com/page3" \
    --concurrency 3 \
    --show-metadata \
    --continue-on-error
```

### Test Extraction Quality
```bash
# Compare different extraction methods
docker compose run --rm url2md4ai \
    test-extraction "https://example.com" --method both --show-diff
```

### Preview Before Converting
```bash
# See what content will be extracted without saving
docker compose run --rm url2md4ai \
    preview "https://example.com" --show-content
```

### Custom Configuration
```bash
# Override default settings
docker run --rm \
    -v "$(pwd)/output:/app/output" \
    -e URL2MD_JAVASCRIPT=false \
    -e URL2MD_CLEAN_CONTENT=false \
    -e URL2MD_TIMEOUT=60 \
    url2md4ai:latest \
    convert "https://example.com" --raw
```

## Available Commands

### convert
Convert a single URL to markdown
```bash
url2md4ai convert "https://example.com" [OPTIONS]
```

**Options:**
- `--show-metadata` - Display conversion metadata
- `--no-js` - Disable JavaScript rendering
- `--force-js` - Force JavaScript rendering
- `--no-clean` - Disable content cleaning
- `--raw` - Raw extraction without LLM optimization
- `--preview` - Preview without saving
- `-o, --output` - Custom output file path

### batch
Convert multiple URLs with parallel processing
```bash
url2md4ai batch "url1" "url2" "url3" [OPTIONS]
```

**Options:**
- `--concurrency` - Number of concurrent conversions (default: 3)
- `--show-metadata` - Display metadata for each conversion
- `--continue-on-error` - Continue processing on failures
- `--output-dir` - Custom output directory

### preview
Preview conversion without saving
```bash
url2md4ai preview "https://example.com" [OPTIONS]
```

**Options:**
- `--show-content` - Show content preview

### test-extraction
Test different extraction methods
```bash
url2md4ai test-extraction "https://example.com" [OPTIONS]
```

**Options:**
- `--method` - Method to test (trafilatura, beautifulsoup, both)
- `--show-diff` - Show comparison between methods

### hash
Generate hash filename for URL
```bash
url2md4ai hash "https://example.com"
```

### config-info
Show current configuration
```bash
url2md4ai config-info [OPTIONS]
```

**Options:**
- `--format` - Output format (text, json)

## Troubleshooting

### Common Issues

**JavaScript content not loading:**
```bash
# Use --force-js and increase timeout
docker compose run --rm url2md4ai \
    convert "https://example.com" --force-js
```

**Large files or slow sites:**
```bash
# Increase timeout
docker run --rm \
    -e URL2MD_TIMEOUT=120 \
    -v "$(pwd)/output:/app/output" \
    url2md4ai:latest \
    convert "https://slow-site.com"
```

**Debug mode:**
```bash
# Enable debug logging
docker run --rm \
    -e URL2MD_LOG_LEVEL=DEBUG \
    -v "$(pwd)/output:/app/output" \
    url2md4ai:latest \
    convert "https://example.com" --show-metadata
```

### Output Files

Generated markdown files are saved to:
- `./output/` directory on your host machine
- Named using URL hash (e.g., `a1b2c3d4e5f6g7h8.md`)
- Each file contains clean, LLM-optimized content

### Performance Tips

1. **Use --no-js for static content** (3x faster)
2. **Adjust concurrency** for batch processing based on your system
3. **Enable caching** for repeated conversions
4. **Use appropriate timeout** values for slow sites 