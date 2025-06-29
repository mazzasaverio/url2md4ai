# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install system dependencies including Playwright requirements
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code first (needed for editable install)
COPY . .

# Install dependencies and the package
RUN uv sync --frozen

# Install Playwright and browsers
RUN uv run playwright install chromium --with-deps

# Create output directory
RUN mkdir -p output

# Set environment variables for url2md4ai
ENV PYTHONPATH=/app/src
ENV URL2MD_OUTPUT_DIR=/app/output
ENV URL2MD_JAVASCRIPT=true
ENV URL2MD_CLEAN_CONTENT=true
ENV URL2MD_LLM_OPTIMIZED=true

# Default command
ENTRYPOINT ["uv", "run", "url2md4ai"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run url2md4ai --help || exit 1

# Labels for better container management
LABEL name="url2md4ai"
LABEL version="1.0.0"
LABEL description="🚀 Lean Python tool for extracting clean, LLM-optimized markdown from web pages"
LABEL maintainer="Saverio Mazza <saverio3107@gmail.com>" 