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

# Install dependencies
RUN uv sync --frozen

# Install Playwright and browsers
RUN uv run playwright install chromium --with-deps

# Copy source code
COPY . .

# Install the package
RUN uv pip install -e .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONPATH=/app/src
ENV URL2MD_OUTPUT_DIR=/app/output

# Default command
ENTRYPOINT ["uv", "run", "url2md4ai"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from structured_output_cookbook.config import Config; Config.from_env()" || exit 1

# Labels for better container management
LABEL name="structured-output-cookbook"
LABEL version="0.1.0"
LABEL description="LLM-powered structured output extraction with predefined and custom schemas"
LABEL maintainer="Saverio Mazza <saverio3107@gmail.com>" 