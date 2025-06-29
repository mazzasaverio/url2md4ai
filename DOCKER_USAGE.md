# Docker Usage Guide

This guide shows how to use Docker with the structured-output-cookbook project using the **correct CLI parameters**.

## Prerequisites

Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Docker Setup Options

### 1. Quick Start with Helper Scripts (Recommended)

**For Development:**
```bash
./scripts/docker-dev.sh
```
This starts an interactive development environment where you can run commands like:
```bash
uv run structured-output list-templates
uv run structured-output extract recipe --input-file examples/recipe.txt
uv run pytest
uv run ruff check .
```

**For Production Use:**
```bash
# Show help
./scripts/docker-run.sh

# Extract using a template (correct syntax)
./scripts/docker-run.sh extract recipe --input-file examples/recipe.txt

# Extract with custom schema  
./scripts/docker-run.sh extract-custom news_article --input-file examples/news_article.txt

# Batch processing
./scripts/docker-run.sh batch-extract examples/recipe.txt examples/product_review.txt recipe

# List available templates
./scripts/docker-run.sh list-templates

# Validate schemas
./scripts/docker-run.sh validate-schemas
```

### 2. Using Docker Compose

**Production service:**
```bash
# Build and show help
docker compose up structured-output-cookbook

# Run specific commands (correct syntax)
docker compose run --rm structured-output-cookbook structured-output extract recipe --input-file examples/recipe.txt
docker compose run --rm structured-output-cookbook structured-output list-templates
docker compose run --rm structured-output-cookbook structured-output extract-custom customer_support --input-file examples/email.txt
```

**Development service:**
```bash
# Start interactive development environment
docker compose run --rm dev
```

### 3. Direct Docker Commands

**Build the image:**
```bash
docker build -t structured-output-cookbook:latest .
```

**Run commands:**
```bash
# Show help
docker run --rm \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/config:/app/config" \
    -v "$(pwd)/examples:/app/examples:ro" \
    structured-output-cookbook:latest

# Extract with template (correct syntax)
docker run --rm \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/config:/app/config" \
    -v "$(pwd)/examples:/app/examples:ro" \
    structured-output-cookbook:latest \
    structured-output extract recipe --input-file examples/recipe.txt

# Extract with custom schema
docker run --rm \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/config:/app/config" \
    -v "$(pwd)/examples:/app/examples:ro" \
    structured-output-cookbook:latest \
    structured-output extract-custom news_article --input-file examples/news_article.txt
```

## Correct CLI Parameter Reference

### extract command
```bash
structured-output extract <TEMPLATE> --input-file <FILE> [OPTIONS]
```
- Template is a **positional argument** (recipe, job, product-review, email, event)
- Use `--input-file` (not `--file`)
- Use `--output` for output file (not `--output-format`)

### extract-custom command  
```bash
structured-output extract-custom <SCHEMA_NAME> --input-file <FILE> [OPTIONS]
```
- Schema name is a **positional argument**
- Use `--input-file` (not `--file`)

### batch-extract command
```bash
structured-output batch-extract <INPUT_FILES...> <TEMPLATE> [OPTIONS]
```
- Input files are **positional arguments** (multiple files allowed)
- Template is the **last positional argument**
- Use `--output-dir` for output directory

### validate-schemas command
```bash
structured-output validate-schemas [--config-dir <DIR>]
```
- Use `--config-dir` (not `--schema-dir`)

## Environment Variables

- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (default: gpt-4o-mini)
- `LOG_LEVEL` (default: INFO for production, DEBUG for dev)
- `MAX_TOKENS` (default: 4000)
- `TEMPERATURE` (default: 0.1)

## Volume Mounts

The Docker setup automatically mounts:
- `./data` → `/app/data` (for output files)
- `./config` → `/app/config` (for custom schemas)  
- `./examples` → `/app/examples` (read-only, for input files)

## Complete Examples

**Extract a recipe:**
```bash
./scripts/docker-run.sh extract recipe --input-file examples/recipe.txt --pretty
```

**Extract with custom schema:**
```bash  
./scripts/docker-run.sh extract-custom product_review --input-file examples/product_review.txt --output data/custom_result.json
```

**Batch processing:**
```bash
./scripts/docker-run.sh batch-extract examples/recipe.txt examples/product_review.txt recipe --output-dir data/batch_results
```

**Validate all schemas:**
```bash
./scripts/docker-run.sh validate-schemas --config-dir config/schemas
```

**Get session statistics:**
```bash
./scripts/docker-run.sh session-stats
```

**Cost analysis:**
```bash
./scripts/docker-run.sh cost-analysis
```

## Common Mistakes to Avoid

❌ **Wrong:** `--file examples/recipe.txt`  
✅ **Correct:** `--input-file examples/recipe.txt`

❌ **Wrong:** `extract --template recipe --file examples/recipe.txt`  
✅ **Correct:** `extract recipe --input-file examples/recipe.txt`

❌ **Wrong:** `batch-extract --input-dir examples --template recipe`  
✅ **Correct:** `batch-extract examples/*.txt recipe`

❌ **Wrong:** `validate-schemas --schema-dir config/schemas`  
✅ **Correct:** `validate-schemas --config-dir config/schemas` 