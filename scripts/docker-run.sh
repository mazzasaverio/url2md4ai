#!/bin/bash

# Docker run script for Structured Output Cookbook
# Usage: ./scripts/docker-run.sh [command] [args...]

set -e

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data config/schemas

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Running Structured Output Cookbook with Docker${NC}"
echo -e "${YELLOW}API Key:${NC} ${OPENAI_API_KEY:0:8}..."

# Check if image exists, build if not
if ! docker image inspect structured-output-cookbook:latest >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Building Docker image...${NC}"
    docker build -t structured-output-cookbook:latest .
fi

# Run the container with the provided command
if [ $# -eq 0 ]; then
    # No arguments provided, show help
    docker run --rm \
        -e OPENAI_API_KEY="$OPENAI_API_KEY" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/config:/app/config" \
        -v "$(pwd)/examples:/app/examples:ro" \
        structured-output-cookbook:latest
else
    # Run with provided arguments
    echo -e "${GREEN}🚀 Running command:${NC} $*"
    docker run --rm \
        -e OPENAI_API_KEY="$OPENAI_API_KEY" \
        -e OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}" \
        -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/config:/app/config" \
        -v "$(pwd)/examples:/app/examples:ro" \
        structured-output-cookbook:latest \
        structured-output "$@"
fi

echo -e "${GREEN}✅ Done!${NC}" 