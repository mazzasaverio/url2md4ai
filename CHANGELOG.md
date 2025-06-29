# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Advanced analytics and monitoring features
- Persistent cache with Redis/SQLite backends
- Streaming support for large responses
- Parallel processing for batch operations

### Changed
- Performance optimizations

## [0.1.1] - TBD

### Fixed
- Fix CI/CD build command from `uvx build` to `uv build`
- Update GitHub Actions workflow for proper package building
- Update Docker documentation with correct CLI parameters (`--input-file` not `--file`)
- Remove obsolete `version` field from docker-compose.yml

### Documentation  
- Add comprehensive Docker usage guide (DOCKER_USAGE.md) with correct CLI syntax
- Fix common CLI parameter mistakes in examples

### Technical
- Remove unnecessary `uv tool install build` from CI pipeline
- Improve automated release process reliability

## [0.1.0] - 2025-06-29

### Added
- **Core extraction functionality** with OpenAI LLMs support
- **Predefined templates** for common use cases:
  - Recipe extraction (`RecipeSchema`)
  - Job description parsing (`JobDescriptionSchema`) 
  - Product review analysis (`ProductReviewSchema`)
  - Email analysis (`EmailSchema`)
  - Event information extraction (`EventSchema`)
- **Custom YAML schema support** for flexible data extraction
- **Intelligent caching system** with configurable TTL
- **Rate limiting** with sliding window algorithm
- **Cost tracking** with accurate real-time pricing for all OpenAI models
- **Robust retry logic** with exponential backoff
- **Input validation** and error handling
- **Comprehensive CLI** with multiple commands:
  - `extract` - Single extraction with predefined templates
  - `extract-custom` - Extraction with custom YAML schemas
  - `batch-extract` - Bulk processing of multiple files
  - `validate-schemas` - YAML schema validation
  - `session-stats` - API usage statistics
  - `cost-analysis` - Cost analysis and model recommendations
- **Docker support** with optimized multi-stage builds using uv
- **Complete test suite** with >80% coverage
- **Professional documentation** with examples and troubleshooting

### Features
- **Ready-to-use templates** for immediate productivity
- **Session statistics** and cost monitoring
- **Model recommendations** based on usage patterns
- **Batch processing** capabilities
- **Cache hit optimization** (30-70% on similar texts)
- **Error recovery** with 95%+ success rate
- **Input length validation** (configurable limits)
- **API key security** with automatic masking in logs

### Technical
- **Python 3.10+** support with full type hints
- **Pydantic v2** for robust data validation
- **OpenAI SDK v1+** compatibility
- **uv package manager** optimization
- **Docker containerization** with security best practices
- **GitHub Actions** CI/CD pipeline
- **Professional logging** with Loguru

### Documentation
- Complete README with quickstart guide
- Docker setup instructions
- Example files for all templates
- Troubleshooting guide
- API reference documentation

[Unreleased]: https://github.com/mazzasaverio/structured-output-cookbook/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mazzasaverio/structured-output-cookbook/releases/tag/v0.1.0 