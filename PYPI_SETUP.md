# PyPI Release Setup Guide

Questa guida descrive come configurare e pubblicare il pacchetto `url2md4ai` su PyPI.

## 🎯 Overview

**url2md4ai** è uno strumento lean per estrarre markdown pulito e ottimizzato per LLM da pagine web. Il processo di rilascio è completamente automatizzato tramite GitHub Actions utilizzando **Trusted Publishing** (raccomandato da PyPI) per una sicurezza ottimale.

## 📋 Prerequisiti

1. **Repository GitHub** con accesso di amministratore
2. **Account PyPI** (crea su [pypi.org](https://pypi.org))
3. **Account Test PyPI** (crea su [test.pypi.org](https://test.pypi.org))

## 🔧 Setup Iniziale

### 1. Configurazione Trusted Publishing su PyPI

#### Per PyPI Production:
1. Vai su [pypi.org](https://pypi.org) e accedi
2. Vai su **Account Settings → Publishing**
3. Clicca **Add a new pending publisher**
4. Inserisci:
   - **PyPI project name**: `url2md4ai`
   - **Owner**: `mazzasaverio`
   - **Repository name**: `url2md4ai`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

#### Per Test PyPI:
1. Vai su [test.pypi.org](https://test.pypi.org) e accedi
2. Ripeti gli stessi passaggi con:
   - **Environment name**: `testpypi`

### 2. Configurazione Environment GitHub

#### Crea Environment "pypi":
1. Vai su **GitHub Repository → Settings → Environments**
2. Clicca **New environment**
3. Nome: `pypi`
4. Aggiungi **Protection rules**:
   - ✅ **Required reviewers** (aggiungi te stesso)
   - ✅ **Restrict pushes that create matching branches**

#### Crea Environment "testpypi":
1. Ripeti per environment `testpypi`
2. Meno restrittivo (per testing)

## 🚀 Processo di Release

### Metodo 1: Automatico (Raccomandato)

```bash
# Bump version e crea release automaticamente
make bump-version VERSION=0.0.1
```

Lo script farà:
1. ✅ Validazione version format
2. ✅ Check branch (deve essere main/master)
3. ✅ Check working directory pulito
4. ✅ Pull latest changes
5. ✅ Run tests
6. ✅ Update version in `__init__.py`
7. ✅ Update CHANGELOG.md
8. ✅ Commit changes
9. ✅ Create e push tag
10. ✅ Trigger GitHub Actions

### Metodo 2: Manuale Step-by-Step

```bash
# 1. Verifica tutto sia ready
make check-release

# 2. Update version manualmente
vim src/url2md4ai/__init__.py
# Cambia: __version__ = "1.0.0"

# 3. Update CHANGELOG.md
vim CHANGELOG.md
# Aggiungi date: ## [1.0.0] - 2024-06-29

# 4. Commit
git add .
git commit -m "🔖 Bump version to 1.0.0"

# 5. Create tag
git tag -a v1.0.0 -m "Release v1.0.0 - LLM-optimized markdown extraction"

# 6. Push
git push origin main
git push origin v1.0.0
```

## 🔄 Workflow Automatico

Una volta pushato il tag, GitHub Actions:

1. **Test Stage**:
   - ✅ Test su Python 3.10, 3.11, 3.12, 3.13
   - ✅ Coverage report
   - ✅ Linting check (ruff, black)
   - ✅ Test CLI functionality

2. **Build Stage**:
   - ✅ Build package con `uv build`
   - ✅ Validate con `twine check`
   - ✅ Upload artifacts

3. **Publish Stage**:
   - ✅ Trusted Publishing su PyPI
   - ✅ Nessun token API necessario
   - ✅ Sicurezza massima

## 🧪 Testing su Test PyPI

Per testare prima della release:

```bash
# Test manuale su Test PyPI
make test-pypi

# Oppure trigger workflow manualmente
# GitHub → Actions → Publish Python Package → Run workflow
```

Poi testa installazione:

```bash
# Installa da Test PyPI
pip install -i https://test.pypi.org/simple/ url2md4ai

# Test delle funzionalità principali
url2md4ai convert "https://example.com" --show-metadata
url2md4ai hash "https://example.com"
url2md4ai --help
```

## 📊 Monitoraggio Release

### Durante la Release:
1. **GitHub Actions**: [Repository Actions](https://github.com/mazzasaverio/url2md4ai/actions)
2. **PyPI Package**: [PyPI url2md4ai](https://pypi.org/project/url2md4ai/)
3. **GitHub Releases**: [Repository Releases](https://github.com/mazzasaverio/url2md4ai/releases)

### Post-Release:
```bash
# Check package su PyPI
pip install url2md4ai

# Verifica versione
python -c "import url2md4ai; print(url2md4ai.__version__)"

# Test CLI completo
url2md4ai convert "https://example.com" --show-metadata
url2md4ai batch "https://example.com" "https://httpbin.org/html" --concurrency 2
url2md4ai preview "https://example.com" --show-content
url2md4ai test-extraction "https://example.com" --method both

# Test installazione con Playwright
playwright install chromium
```

## 🛠️ Comandi di Release Disponibili

```bash
# Sviluppo e Test
make dev-setup              # Setup completo sviluppo con uv
make test                   # Run pytest con coverage
make lint                   # Run ruff e black
make check-release          # Verifica ready per release

# Build e Package
make build-package          # Build con uv build
make clean-dist            # Pulizia dist files
make validate-package       # Validate con twine check

# Release
make bump-version VERSION=X.Y.Z  # Release automatico
make test-pypi             # Upload su TestPyPI
make release-pypi          # Release finale su PyPI

# Utilities
make docker-build          # Build Docker image
make docker-test           # Test Docker functionality
```

## 🧪 Pre-Release Checklist

Prima di ogni release, verifica:

```bash
# 1. Test completi
make test
make lint

# 2. Test CLI functionality
uv run url2md4ai convert "https://example.com" --show-metadata
uv run url2md4ai batch "https://example.com" "https://httpbin.org/html"

# 3. Test Docker
docker build -t url2md4ai .
docker run --rm url2md4ai --help

# 4. Test installazione da wheel
make build-package
pip install dist/url2md4ai-*.whl
url2md4ai --help

# 5. Test documentazione
# Verifica README.md, DOCKER_USAGE.md, examples/
```

## 📦 Package Information

### Struttura Package:
```
url2md4ai/
├── src/url2md4ai/
│   ├── __init__.py          # Version info
│   ├── cli.py              # CLI entry point
│   ├── converter.py        # Core conversion logic
│   ├── config.py           # Configuration management
│   └── utils/              # Utilities (logger, rate_limiter)
├── examples/               # Usage examples
├── tests/                  # Test suite
└── pyproject.toml         # Package configuration
```

### Dependencies:
- **Core**: trafilatura, playwright, beautifulsoup4, html2text
- **CLI**: click, loguru
- **Dev**: pytest, ruff, black, mypy

## 🔒 Sicurezza e Best Practices

### Trusted Publishing vs API Tokens:
- ✅ **Trusted Publishing**: Sicurezza massima, gestione automatica
- ❌ **API Tokens**: Meno sicuro, gestione manuale

### Security Checklist:
1. **Branch Protection**: Solo da main/master
2. **Environment Protection**: Required reviewers per pypi environment
3. **Dependency Security**: uv per dependency management sicuro
4. **Version Pinning**: Lock file con uv.lock
5. **Semantic Versioning**: Sempre (MAJOR.MINOR.PATCH)
6. **Changelog**: Aggiornato ad ogni release

## 🐛 Troubleshooting

### Errore: "Package already exists"
```bash
# Incrementa version
make bump-version VERSION=1.0.1
```

### Errore: "Trusted publisher not found"
- Verifica configurazione PyPI
- Check nome repository/owner esatti
- Verifica workflow name: `release.yml`
- Check environment name: `pypi` o `testpypi`

### Errore: "Tests failed"
```bash
# Debug locale
make test
make lint

# Test specifici
uv run pytest tests/unit/test_config.py -v
uv run pytest tests/ --cov=src/url2md4ai
```

### Errore: "Docker build failed"
```bash
# Test Dockerfile locale
docker build -t url2md4ai:debug .
docker run --rm url2md4ai:debug --help
```

### Errore: "Import failed"
```bash
# Check package structure
python -c "from url2md4ai import URLToMarkdownConverter, Config; print('OK')"

# Check CLI entry point
which url2md4ai
url2md4ai --version
```

## 🎯 Next Steps Dopo Release

1. **Annuncio**: Condividi su social media e community
2. **Documentation**: Aggiorna wiki/docs se necessario
3. **Feedback**: Monitor GitHub issues per bug reports
4. **Metriche**: Track downloads su PyPI
5. **Roadmap**: Plan prossime features nel CHANGELOG.md 