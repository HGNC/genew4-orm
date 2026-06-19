# Development Workflow

This guide explains the complete development and deployment workflow for genew4-orm, from local development to automated releases.

## Overview

genew4-orm uses GitHub Actions for continuous integration, automated releases, and documentation deployment.

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                            │
│  Local Development ────────► GitHub Repository ────────► GitHub Actions              │
│                                                            │
│   ↓                                                        │                          ↓
│   Feature Branch                          CI Workflows              │
│   ↓                                     ↓
│   Pull Request                             Merge to main                │
│                                                            │
│                                         Semantic Release              Docs Deploy               │
│                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

Before starting development, ensure you have:

1. **Python 3.13+** installed
2. **uv** installed (recommended package manager)
3. **Git** configured with your credentials
4. **GitHub account** with repository access

## Local Development Setup

```bash
# Clone the repository
git clone https://github.com/HGNC/genew4-orm.git
cd genew4-orm

# Install development dependencies
make dev-setup
# Equivalent to:
# make venv
# make install
# make pre-commit
```

## Development Process

### 1. Create a Feature Branch

```bash
# Start from main branch
git checkout main
git pull origin main

# Create a feature branch for your work
git checkout -b feature/my-feature
```

### 2. Make Changes and Test Locally

```bash
# Run linting (fixes issues automatically)
make lint

# Run tests (requires PostgreSQL)
make test
# Or run specific test categories:
make test-unit
make test-integration
make test-e2e

# Check coverage
make test-cov
open htmlcov/index.html
```

### 3. Commit with Conventional Messages

Use conventional commit messages for semantic versioning:

```bash
# Stage your changes
git add .

# Commit with appropriate type
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in gene query"
git commit -m "docs: update README with workflow info"
```

| Type | Description | Version Bump |
|-------|-------------|--------------|
| `feat:` | New feature | **MINOR** (0.x.0 → 0.(x+1).0) |
| `fix:` | Bug fix | **PATCH** (0.x.0 → 0.x.(x+1).0) |
| `build:` | Build system changes | **PATCH** |
| `chore:` | Maintenance tasks | **PATCH** |
| `docs:` | Documentation only | **PATCH** |
| `perf:` | Performance improvements | **PATCH** |
| `refactor:` | Code refactoring | **PATCH** |
| `style:` | Code style changes | **PATCH** |
| `test:` | Adding/updating tests | **PATCH** |

### 4. Push to GitHub

```bash
# Push your feature branch
git push origin feature/my-feature
```

### 5. Create Pull Request

1. Go to: https://github.com/HGNC/genew4-orm
2. Click "Compare & pull request"
3. Create PR from your feature branch to `main`

## What Happens Automatically (GitHub Actions)

### On Pull Request Creation

When you create a PR, the **CI workflow** runs automatically:

```yaml
# .github/workflows/ci.yml
CI Workflow Steps:
├── Checkout code
├── Install dependencies (uv, pytest, ruff, mypy, black, isort)
├── Lint (ruff, mypy, black, isort)
├── Create database schema (Alembic migrations)
├── Run unit tests
├── Run integration tests (with PostgreSQL)
├── Run e2e tests
└── Generate coverage report
```

**All checks must pass** before the PR can be merged:
- ✅ Ruff linting passes
- ✅ MyPy type checking passes
- ✅ Black formatting is correct
- ✅ Isort imports are sorted
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ E2E tests pass
- ✅ Coverage threshold met

### On Merge to Main Branch

When your PR is merged to `main`:

#### 1. Semantic Release Workflow Triggers

The **Release workflow** runs automatically:

```yaml
# .github/workflows/release.yml
Release Workflow Steps:
├── Analyze commit messages (python-semantic-release)
├── Determine new version from conventional commits
├── Create git tag (e.g., v0.2.0)
├── Update CHANGELOG.md
├── Create GitHub Release with release notes
└── Update README.md version badge
```

#### 2. Documentation Deployment Triggers

The **Docs workflow** runs automatically:

```yaml
# .github/workflows/docs.yml
Docs Workflow Steps:
├── Build MkDocs with Material theme
├── Deploy to GitHub Pages (hgnc.github.io/genew4-orm)
```

### Result: Complete Deployment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                             │
│   PR merged to main                                    │
│     ↓                                                   │
│     │                                                   │
│     │                              ┌─────────────────────┐      │
│     │                              │ Semantic Release    │      │
│     │                              │ • Version bumped    │      │
│     │                              │ • Git tag created  │      │
│     │                              │ • GitHub release    │      │
│     │                              │ • README updated    │      │
│     │                              └─────────────────────┘      │
│     │                                                   │
│     │                              ┌─────────────────────┐      │
│     ↓                              │ Docs Deployment    │      │
│     │                              │ • MkDocs built    │      │
│     │                              │ • GitHub Pages     │      │
│     │                              └─────────────────────┘      │
│     │                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Users can now:**
- Download the new release from GitHub Releases
- Use the updated documentation at https://hgnc.github.io/genew4-orm
- Install the latest version: `pip install genew4-orm==X.Y.Z`

## Pre-commit Hooks (Optional)

For automatic code quality checks before committing:

```bash
# Install pre-commit hooks
make pre-commit

# Now every git commit will automatically:
# - Run ruff to check and fix issues
# - Run mypy for type checking
# - Run black for formatting
# - Run isort for import sorting
```

## CI Status Badges

The GitHub Actions status is displayed on your repository:

- **CI**: All linting and testing status
- **Release**: Latest version from semantic release
- **Docs**: Documentation build and deployment status
- **Coverage**: Code coverage percentage

## Quick Reference Commands

```bash
# Development
make dev-setup              # Full setup
make lint                   # Run all linters
make test                   # Run all tests
make format                  # Format code

# Database (for integration tests)
make db-up                  # Start PostgreSQL
make db-down                # Stop PostgreSQL
make db-shell               # Connect to psql

# Documentation
make docs-serve            # Serve docs locally
make docs-build            # Build docs

# Cleanup
make clean                  # Remove build artifacts
```

## Troubleshooting

### PR Checks Failing

If CI checks fail on your PR:

1. **Check the Actions tab** on GitHub for detailed error logs
2. **Run locally**:
   ```bash
   make lint
   make test
   ```
3. **Fix issues** and commit with conventional message
4. **Push** new commit

### Integration Tests Failing Locally

Integration tests require PostgreSQL:

```bash
# Option 1: Use Docker (matches CI)
docker-compose up -d postgres
pytest tests/integration/

# Option 2: Use remote PostgreSQL
# Set DATABASESETTINGS__PG_HOST to your remote database
# Then run tests normally
```

### Release Not Creating

Releases only trigger on push to `main` branch. Ensure:
- PR is merged to `main` (not just committed)
- Commit uses conventional message format (see table above)
- Commit is from a PR (not directly to main)

## Best Practices

1. **Feature Branches**: Always work on feature branches, never directly on `main` or `develop`
2. **Conventional Commits**: Use proper prefixes for automatic versioning
3. **Local Testing**: Always run `make lint` and `make test` before pushing
4. **Small PRs**: Keep PRs focused on a single feature for easier review
5. **Descriptive PRs**: Use clear titles describing what and why
6. **Documentation**: Update docs when adding features that change usage
