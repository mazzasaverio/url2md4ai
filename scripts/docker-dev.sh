#!/bin/bash

# Docker development environment script for url2md4ai
# Usage: ./scripts/docker-dev.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🛠️  Starting url2md4ai Development Environment${NC}"

# Build image if it doesn't exist
if ! docker image inspect url2md4ai:latest >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Building Docker image...${NC}"
    docker build -t url2md4ai:latest .
fi

# Set development environment variables
export URL2MD_LOG_LEVEL=DEBUG
export URL2MD_CLEAN_CONTENT=true
export URL2MD_LLM_OPTIMIZED=true
export URL2MD_USE_TRAFILATURA=true
export URL2MD_JAVASCRIPT=true

echo -e "${BLUE}🔧 Development Configuration:${NC}"
echo -e "   Log Level: DEBUG"
echo -e "   Clean Content: ${URL2MD_CLEAN_CONTENT}"
echo -e "   LLM Optimized: ${URL2MD_LLM_OPTIMIZED}"
echo ""

# Run development container
echo -e "${GREEN}🚀 Starting interactive development shell...${NC}"
echo -e "${YELLOW}💡 You can now run commands like:${NC}"
echo "   uv run url2md4ai convert \"https://example.com\" --show-metadata"
echo "   uv run url2md4ai batch \"https://site1.com\" \"https://site2.com\""
echo "   uv run url2md4ai test-extraction \"https://example.com\" --method both"
echo "   uv run pytest"
echo "   uv run ruff check ."
echo ""

docker run -it --rm \
    -e URL2MD_CLEAN_CONTENT="$URL2MD_CLEAN_CONTENT" \
    -e URL2MD_LLM_OPTIMIZED="$URL2MD_LLM_OPTIMIZED" \
    -e URL2MD_USE_TRAFILATURA="$URL2MD_USE_TRAFILATURA" \
    -e URL2MD_JAVASCRIPT="$URL2MD_JAVASCRIPT" \
    -e URL2MD_LOG_LEVEL="$URL2MD_LOG_LEVEL" \
    -v "$(pwd):/app" \
    -v /app/.venv \
    --workdir /app \
    url2md4ai:latest \
    /bin/bash 