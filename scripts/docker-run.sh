#!/bin/bash

# Docker run script for url2md4ai
# Usage: ./scripts/docker-run.sh [command] [args...]

set -e

# Create output directory if it doesn't exist
mkdir -p output

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Running url2md4ai with Docker${NC}"

# Check if image exists, build if not
if ! docker image inspect url2md4ai:latest >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Building Docker image...${NC}"
    docker build -t url2md4ai:latest .
fi

# Set default environment variables for LLM optimization
export URL2MD_CLEAN_CONTENT="${URL2MD_CLEAN_CONTENT:-true}"
export URL2MD_LLM_OPTIMIZED="${URL2MD_LLM_OPTIMIZED:-true}"
export URL2MD_USE_TRAFILATURA="${URL2MD_USE_TRAFILATURA:-true}"
export URL2MD_JAVASCRIPT="${URL2MD_JAVASCRIPT:-true}"
export URL2MD_HEADLESS="${URL2MD_HEADLESS:-true}"
export URL2MD_OUTPUT_DIR="/app/output"
export URL2MD_LOG_LEVEL="${URL2MD_LOG_LEVEL:-INFO}"

# Display configuration
echo -e "${BLUE}🔧 Configuration:${NC}"
echo -e "   Clean Content: ${URL2MD_CLEAN_CONTENT}"
echo -e "   LLM Optimized: ${URL2MD_LLM_OPTIMIZED}"
echo -e "   Use Trafilatura: ${URL2MD_USE_TRAFILATURA}"
echo -e "   JavaScript: ${URL2MD_JAVASCRIPT}"
echo ""

# Run the container with the provided command
if [ $# -eq 0 ]; then
    # No arguments provided, show help
    docker run --rm \
        -e URL2MD_CLEAN_CONTENT="$URL2MD_CLEAN_CONTENT" \
        -e URL2MD_LLM_OPTIMIZED="$URL2MD_LLM_OPTIMIZED" \
        -e URL2MD_USE_TRAFILATURA="$URL2MD_USE_TRAFILATURA" \
        -e URL2MD_JAVASCRIPT="$URL2MD_JAVASCRIPT" \
        -e URL2MD_HEADLESS="$URL2MD_HEADLESS" \
        -e URL2MD_OUTPUT_DIR="$URL2MD_OUTPUT_DIR" \
        -e URL2MD_LOG_LEVEL="$URL2MD_LOG_LEVEL" \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/examples:/app/examples:ro" \
        url2md4ai:latest
else
    # Run with provided arguments
    echo -e "${GREEN}🚀 Running command:${NC} url2md4ai $*"
    docker run --rm \
        -e URL2MD_CLEAN_CONTENT="$URL2MD_CLEAN_CONTENT" \
        -e URL2MD_LLM_OPTIMIZED="$URL2MD_LLM_OPTIMIZED" \
        -e URL2MD_USE_TRAFILATURA="$URL2MD_USE_TRAFILATURA" \
        -e URL2MD_JAVASCRIPT="$URL2MD_JAVASCRIPT" \
        -e URL2MD_HEADLESS="$URL2MD_HEADLESS" \
        -e URL2MD_OUTPUT_DIR="$URL2MD_OUTPUT_DIR" \
        -e URL2MD_LOG_LEVEL="$URL2MD_LOG_LEVEL" \
        -e URL2MD_TIMEOUT="${URL2MD_TIMEOUT:-30}" \
        -e URL2MD_MAX_RETRIES="${URL2MD_MAX_RETRIES:-3}" \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/examples:/app/examples:ro" \
        url2md4ai:latest \
        "$@"
fi

echo -e "${GREEN}✅ Done! Check output/ directory for generated files.${NC}" 