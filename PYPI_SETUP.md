# PyPI Release Setup Guide

Questa guida descrive come configurare e pubblicare il pacchetto `structured-output-cookbook` su PyPI.

## 🎯 Overview

Il processo di rilascio è completamente automatizzato tramite GitHub Actions utilizzando **Trusted Publishing** (raccomandato da PyPI) per una sicurezza ottimale.

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
   - **PyPI project name**: `structured-output-cookbook`
   - **Owner**: `mazzasaverio`
   - **Repository name**: `structured-output-cookbook`
   - **Workflow name**: `pypi-publish.yml`
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
make bump-version VERSION=0.1.0
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
vim src/structured_output_cookbook/__init__.py
# Cambia: __version__ = "0.1.0"

# 3. Update CHANGELOG.md
vim CHANGELOG.md
# Aggiungi date: ## [0.1.0] - 2024-01-15

# 4. Commit
git add .
git commit -m "🔖 Bump version to 0.1.0"

# 5. Create tag
git tag -a v0.1.0 -m "Release v0.1.0"

# 6. Push
git push origin main
git push origin v0.1.0
```

## 🔄 Workflow Automatico

Una volta pushato il tag, GitHub Actions:

1. **Test Stage**:
   - ✅ Test su Python 3.10, 3.11, 3.12, 3.13
   - ✅ Coverage report
   - ✅ Linting check

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
pip install -i https://test.pypi.org/simple/ structured-output-cookbook
```

## 📊 Monitoraggio Release

### Durante la Release:
1. **GitHub Actions**: [Repository Actions](https://github.com/mazzasaverio/structured-output-cookbook/actions)
2. **PyPI Package**: [PyPI structured-output-cookbook](https://pypi.org/project/structured-output-cookbook/)
3. **GitHub Releases**: [Repository Releases](https://github.com/mazzasaverio/structured-output-cookbook/releases)

### Post-Release:
```bash
# Check package su PyPI
pip install structured-output-cookbook

# Verifica versione
python -c "import structured_output_cookbook; print(structured_output_cookbook.__version__)"

# Test CLI
structured-output --help
```

## 🛠️ Comandi Utili

```bash
# Sviluppo
make dev-setup              # Setup completo sviluppo
make test                   # Run tests
make check-release          # Verifica ready per release

# Release
make bump-version VERSION=X.Y.Z  # Release automatico
make build-package          # Build locale
make clean-dist            # Pulizia dist files

# Debugging
make test-pypi             # Test su TestPyPI
make upload-pypi           # Upload manuale (backup)
```

## 🔒 Sicurezza

### Trusted Publishing vs API Tokens:
- ✅ **Trusted Publishing**: Sicurezza massima, gestione automatica
- ❌ **API Tokens**: Meno sicuro, gestione manuale

### Best Practices:
1. **Branch Protection**: Solo da main/master
2. **Environment Protection**: Required reviewers
3. **Signed Commits**: Raccomandato
4. **Semantic Versioning**: Sempre
5. **Changelog**: Aggiornato ad ogni release

## 🐛 Troubleshooting

### Errore: "Package already exists"
```bash
# Incrementa version
make bump-version VERSION=0.1.1
```

### Errore: "Trusted publisher not found"
- Verifica configurazione PyPI
- Check nome repository/owner
- Verifica workflow name

### Errore: "Tests failed"
```bash
# Debug locale
make test
make lint
```

### Errore: "Environment not found"
- Crea environment su GitHub
- Verifica nome environment nel workflow

## 📈 Metriche Post-Release

Monitor su:
1. **PyPI Downloads**: [pypistats.org](https://pypistats.org/packages/structured-output-cookbook)
2. **GitHub Traffic**: Repository → Insights → Traffic
3. **Issues/Discussions**: Repository → Issues

## 🔄 Aggiornamenti Futuri

Per nuove release:
1. Sviluppa features
2. Update CHANGELOG.md
3. `make bump-version VERSION=X.Y.Z`
4. Monitor workflow
5. Verify su PyPI

---

## 🎉 Congratulazioni!

Il tuo pacchetto è ora su PyPI! 🚀

```bash
pip install structured-output-cookbook
``` 