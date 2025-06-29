#!/bin/bash
set -e

# Release script for structured-output-cookbook
# Usage: ./scripts/release.sh [version]

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.0"
    exit 1
fi

VERSION=$1
CURRENT_BRANCH=$(git branch --show-current)

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format. Use semantic versioning (e.g., 0.1.0)"
    exit 1
fi

echo "🚀 Starting release process for version $VERSION"

# Check we're on main/master branch
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "❌ Please switch to main/master branch before releasing"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo "❌ Working directory is not clean. Please commit your changes."
    git status --porcelain
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin $CURRENT_BRANCH

# Run tests
echo "🧪 Running tests..."
if command -v uv &> /dev/null; then
    uv run pytest
else
    python -m pytest
fi

if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please fix them before releasing."
    exit 1
fi

# Update version in __init__.py
echo "📝 Updating version to $VERSION..."
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/structured_output_cookbook/__init__.py

# Check if backup file exists and remove it (for cross-platform compatibility)
if [ -f "src/structured_output_cookbook/__init__.py.bak" ]; then
    rm src/structured_output_cookbook/__init__.py.bak
fi

# Update CHANGELOG.md date
TODAY=$(date +%Y-%m-%d)
sed -i.bak "s/## \[${VERSION}\] - .*/## [${VERSION}] - ${TODAY}/" CHANGELOG.md

# Check if backup file exists and remove it
if [ -f "CHANGELOG.md.bak" ]; then
    rm CHANGELOG.md.bak
fi

echo "📝 Please review the CHANGELOG.md and ensure all changes for version $VERSION are documented"
echo "Current changelog entry:"
echo "========================="
grep -A 20 "## \[${VERSION}\]" CHANGELOG.md | head -21
echo "========================="
echo ""
read -p "Press Enter to continue if the changelog looks good, or Ctrl+C to abort..."

# Commit version bump
echo "💾 Committing version bump..."
git add src/structured_output_cookbook/__init__.py CHANGELOG.md
git commit -m "🔖 Bump version to $VERSION

- Update version in __init__.py
- Update CHANGELOG.md with release date"

# Create and push tag
echo "🏷️  Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "🚀 Release version $VERSION

$(grep -A 10 "## \[${VERSION}\]" CHANGELOG.md | tail -n +2 | head -10)"

echo "📤 Pushing changes and tag..."
git push origin $CURRENT_BRANCH
git push origin "v$VERSION"

echo "✅ Release $VERSION initiated!"
echo ""
echo "🔗 GitHub Actions: https://github.com/mazzasaverio/structured-output-cookbook/actions"
echo "📦 PyPI: https://pypi.org/project/structured-output-cookbook/"
echo ""
echo "The GitHub Actions workflow will:"
echo "  1. ✅ Run tests on multiple Python versions"
echo "  2. 📦 Build the package"
echo "  3. 🚀 Publish to PyPI (if tag push)"
echo "  4. 📝 Create GitHub release with changelog"
echo ""
echo "Monitor the workflow progress at the GitHub Actions link above." 