#!/bin/bash

# Docker development environment script
# Usage: ./scripts/docker-dev.sh

set -e

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🛠️  Starting Structured Output Cookbook Development Environment${NC}"
echo -e "${YELLOW}API Key:${NC} ${OPENAI_API_KEY:0:8}..."

# Build image if it doesn't exist
if ! docker image inspect structured-output-cookbook:latest >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Building Docker image...${NC}"
    docker build -t structured-output-cookbook:latest .
fi

# Run development container
echo -e "${GREEN}🚀 Starting interactive development shell...${NC}"
echo -e "${YELLOW}💡 You can now run commands like:${NC}"
echo "   uv run structured-output list-templates"
echo "   uv run pytest"
echo "   uv run ruff check ."
echo ""

docker run -it --rm \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}" \
    -e LOG_LEVEL="${LOG_LEVEL:-DEBUG}" \
    -v "$(pwd):/app" \
    -v /app/.venv \
    --workdir /app \
    structured-output-cookbook:latest \
    /bin/bash 