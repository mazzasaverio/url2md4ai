# Structured Output Cookbook - Makefile
# Provides convenient commands for development and usage

.PHONY: help install dev test lint format clean docker-build docker-run docker-dev format-check lint-check pre-commit check quality

# Default target
help: ## Show this help message
	@echo "🧑‍🍳 Structured Output Cookbook - Available Commands"
	@echo "================================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Setup
install: ## Install dependencies with uv
	@echo "📦 Installing dependencies..."
	uv sync

dev: install ## Install development dependencies
	@echo "🛠️  Installing development dependencies..."
	uv sync --all-extras

# Code Quality - Core Commands
format: ## Format code with black and ruff
	@echo "💄 Formatting code..."
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

format-check: ## Check if code needs formatting
	@echo "🔍 Checking code formatting..."
	uv run black --check --diff src/ tests/
	uv run ruff check src/ tests/

lint: ## Run all linters
	@echo "🔍 Running linters..."
	uv run ruff check src/ tests/
	uv run mypy src/ --ignore-missing-imports

lint-fix: ## Fix all linting issues
	@echo "🔧 Fixing linting issues..."
	uv run ruff check --fix src/ tests/
	uv run black src/ tests/

# Comprehensive Quality Checks
pre-commit: format lint ## Run all pre-commit checks (format + lint)
	@echo "✅ Pre-commit checks completed!"

check: pre-commit test ## Run all quality checks (format, lint, tests)
	@echo "✅ All quality checks passed!"

quality: clean-cache pre-commit test ## Full quality check with cache cleanup
	@echo "✅ Full quality check completed!"

# Tests
test: ## Run tests
	@echo "🧪 Running tests..."
	uv run pytest

test-cov: ## Run tests with coverage
	@echo "📊 Running tests with coverage..."
	uv run pytest --cov=src/structured_output_cookbook --cov-report=html

test-verbose: ## Run tests with verbose output
	@echo "🧪 Running tests (verbose)..."
	uv run pytest -v

# CLI Commands (with quality checks)
list-templates: pre-commit ## List available predefined templates
	@echo "📋 Available templates:"
	uv run structured-output list-templates

list-schemas: pre-commit ## List available custom schemas
	@echo "📋 Available schemas:"
	uv run structured-output list-schemas

example-recipe: pre-commit ## Run recipe extraction example
	@echo "🍝 Running recipe extraction example..."
	uv run structured-output extract recipe --input-file examples/recipe.txt --pretty

example-job: pre-commit ## Run job description extraction example
	@echo "💼 Running job description extraction example..."
	uv run structured-output extract job --input-file examples/job_description.txt --pretty

example-news: pre-commit ## Run news article extraction example
	@echo "📰 Running news article extraction example..."
	uv run structured-output extract-custom news_article --input-file examples/news_article.txt --pretty

example-email: pre-commit ## Run email extraction example
	@echo "📧 Running email extraction example..."
	uv run structured-output extract email --text "Subject: Meeting Tomorrow\nFrom: john@company.com\nHi team, we have an important meeting tomorrow at 2 PM in conference room A. Please bring your reports." --pretty

example-event: pre-commit ## Run event extraction example
	@echo "🎉 Running event extraction example..."
	uv run structured-output extract event --text "Annual Tech Conference 2024 - Join us on March 15th at San Francisco Convention Center from 9 AM to 6 PM. Registration required." --pretty

example-product-review: pre-commit ## Run product review extraction example
	@echo "⭐ Running product review extraction example..."
	uv run structured-output extract product-review --text "Amazing laptop! The new MacBook Pro is incredible. 5 stars. Great performance, excellent display. Worth every penny. Highly recommended for developers." --pretty

# Docker Commands
docker-build: check ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t structured-output-cookbook:latest .

docker-run: ## Run with Docker (requires OPENAI_API_KEY env var)
	@echo "🐳 Running with Docker..."
	./scripts/docker-run.sh

docker-dev: ## Start development environment with Docker
	@echo "🛠️  Starting Docker development environment..."
	./scripts/docker-dev.sh

docker-compose-up: ## Start services with docker-compose
	@echo "🐳 Starting with docker-compose..."
	docker-compose up --build

docker-compose-run: ## Run command with docker-compose
	@echo "🐳 Running command with docker-compose..."
	docker-compose run --rm structured-output-cookbook $(ARGS)

# Examples with Docker
docker-example-recipe: ## Run recipe extraction example with Docker
	@echo "🍝 Running recipe extraction example with Docker..."
	./scripts/docker-run.sh extract recipe --input-file examples/recipe.txt --pretty

docker-example-job: ## Run job description extraction example with Docker
	@echo "💼 Running job description extraction example with Docker..."
	./scripts/docker-run.sh extract job --input-file examples/job_description.txt --pretty

docker-list-templates: ## List templates with Docker
	@echo "📋 Listing templates with Docker..."
	./scripts/docker-run.sh list-templates

# New CLI Commands
validate-schemas: pre-commit ## Validate all custom YAML schemas
	@echo "🔍 Validating schemas..."
	uv run structured-output validate-schemas

session-stats: pre-commit ## Show session statistics
	@echo "📊 Showing session statistics..."
	uv run structured-output session-stats

cost-analysis: pre-commit ## Show cost analysis and recommendations
	@echo "💰 Showing cost analysis..."
	uv run structured-output cost-analysis

# Batch processing examples
batch-example: pre-commit ## Run batch extraction example
	@echo "🔄 Running batch extraction example..."
	mkdir -p examples/batch_input examples/batch_output
	echo "Sample recipe 1: Pasta with tomato sauce" > examples/batch_input/recipe1.txt
	echo "Sample recipe 2: Chicken curry with rice" > examples/batch_input/recipe2.txt
	uv run structured-output batch-extract examples/batch_input/*.txt recipe --output-dir examples/batch_output

# Cleanup
clean-cache: ## Clean up cache files
	@echo "🧹 Cleaning cache files..."
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean: clean-cache ## Clean up build artifacts and cache
	@echo "🧹 Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/

clean-all: clean clean-dist ## Clean everything including distribution files
	@echo "🧹 Deep cleaning complete!"

clean-docker: ## Clean up Docker images and containers
	@echo "🐳 Cleaning up Docker..."
	docker system prune -f
	docker image prune -f

# Environment Setup
env-example: ## Create example environment file
	@echo "📝 Creating example environment file..."
	@echo "# OpenAI Configuration (Required)" > .env.example
	@echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env.example
	@echo "" >> .env.example
	@echo "# Optional Configuration" >> .env.example
	@echo "OPENAI_MODEL=gpt-4o-mini" >> .env.example
	@echo "LOG_LEVEL=INFO" >> .env.example
	@echo "MAX_TOKENS=4000" >> .env.example
	@echo "TEMPERATURE=0.1" >> .env.example
	@echo "✅ Created .env.example file"

check-env: ## Check if required environment variables are set
	@echo "🔍 Checking environment variables..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "❌ OPENAI_API_KEY is not set"; \
		echo "Please set your OpenAI API key:"; \
		echo "export OPENAI_API_KEY='your-api-key-here'"; \
		exit 1; \
	else \
		echo "✅ OPENAI_API_KEY is set"; \
	fi

# Release Management
bump-version: check ## Bump version and create release (usage: make bump-version VERSION=0.1.0)
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Please specify VERSION. Usage: make bump-version VERSION=0.1.0"; \
		exit 1; \
	fi
	./scripts/release.sh $(VERSION)

build-package: check ## Build package for PyPI
	@echo "📦 Building package..."
	uv build
	uvx twine check dist/*

test-pypi: check ## Upload to Test PyPI
	@echo "🧪 Uploading to Test PyPI..."
	uvx twine upload --repository testpypi dist/*

upload-pypi: check ## Upload to PyPI (manual backup)
	@echo "📤 Uploading to PyPI..."
	uvx twine upload dist/*

check-release: check ## Check if package is ready for release
	@echo "🔍 Checking release readiness..."
	uv build
	uvx twine check dist/*
	@echo "✅ Package ready for release!"

clean-dist: ## Clean distribution files
	@echo "🧹 Cleaning distribution files..."
	rm -rf dist/ build/ *.egg-info/

# Release (legacy)
build: check ## Build the package
	@echo "📦 Building package..."
	uv build

publish: build ## Publish to PyPI (requires authentication)
	@echo "🚀 Publishing to PyPI..."
	uv publish

# Quick Start
quick-start: install check-env example-recipe ## Quick start: install, check env, and run example
	@echo "🎉 Quick start completed successfully!"
	@echo "Try running: make list-templates"

# Development workflow
dev-setup: dev env-example ## Setup development environment
	@echo "🛠️  Development environment setup complete!"
	@echo "Don't forget to:"
	@echo "1. Copy .env.example to .env and add your OpenAI API key"
	@echo "2. Run 'make check-env' to verify setup"
	@echo "3. Run 'make check' to run all quality checks"

# Fix all code issues in one command
fix: ## Fix all formatting and linting issues
	@echo "🔧 Fixing all code issues..."
	@echo "Step 1: Formatting with black..."
	uv run black src/ tests/
	@echo "Step 2: Fixing linting issues with ruff..."
	uv run ruff check --fix src/ tests/
	@echo "Step 3: Running tests to verify..."
	uv run pytest
	@echo "✅ All issues fixed!" 