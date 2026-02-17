# genew4-orm

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

Python ORM for the genew4 PostgreSQL database.

## Features

- Type-safe models with Pydantic validation
- Read-only by default (safe mode)
- Full CRUD when needed
- Audit logging for all writes
- Comprehensive test suite with high coverage
- Async support

## Installation

```bash
uv add genew4-orm
```

## Quick Example

```python
from genew4_orm import get_readonly_session
from genew4_orm.models import Gene
from sqlmodel import select

with get_readonly_session() as session:
    genes = session.exec(select(Gene).limit(10)).all()
    for gene in genes:
        print(f"{gene.approved_symbol}: {gene.approved_name}")
```

## Configuration

Set environment variables (see `.env.example`):

```bash
# Database connection
GENEW4_DB_HOST=localhost
GENEW4_DB_PORT=5432
GENEW4_DB_NAME=genew4
GENEW4_DB_USER=your_user
GENEW4_DB_PASSWORD=your_password
```

## Usage

### Read-Only Sessions (Recommended)

```python
from genew4_orm import get_readonly_session
from genew4_orm.models import Gene, User
from sqlmodel import select

with get_readonly_session() as session:
    # Query genes
    gene = session.get(Gene, 1)

    # Query with filters
    genes = session.exec(
        select(Gene).where(Gene.approved_symbol == "BRCA1")
    ).all()

    # Join with related models
    results = session.exec(
        select(Gene, User).join(User)
    ).all()
```

### Read-Write Sessions (Audit Logged)

```python
from genew4_orm import get_readwrite_session
from genew4_orm.models import Gene
from sqlmodel import select

with get_readwrite_session(user_id="user-123") as session:
    gene = session.get(Gene, 1)
    gene.approved_name = "Updated Name"
    session.add(gene)
    session.commit()
    # All writes are logged to the audit table
```

### Async Sessions

```python
from genew4_orm import get_async_readonly_session
from genew4_orm.models import Gene
from sqlmodel import select

async with get_async_readonly_session() as session:
    genes = await session.exec(select(Gene).limit(10))
    async for gene in genes:
        print(gene.approved_symbol)
```

## Available Models

- **Gene** - Gene information
- **User** - User accounts
- **Reminder** - User reminders

## Development

### Setup

```bash
# Install dependencies
uv sync --group dev

# Copy environment template and configure
cp .env.example .env
# Edit .env with your database credentials
```

### Continuous Integration

This project uses GitHub Actions for CI/CD:

- **Linting**: ruff, mypy, black, isort run on every push
- **Testing**: All tests run automatically (unit, integration, e2e)
- **Database**: PostgreSQL container spun up for integration tests
- **Releases**: Semantic versioning via conventional commits
- **Documentation**: Auto-deployed to GitHub Pages

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage (generates HTML report in htmlcov/)
pytest --cov=genew4_orm --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_gene_model

# Run tests in parallel (faster on multi-core)
pytest -n auto

# Run with verbose output
pytest -v

# Run only tests matching a pattern
pytest -k "test_user"
```

## Contributing Workflow

```bash
# 1. Create a feature branch
git checkout -b feature/my-changes

# 2. Make your changes
# Edit code, fix bugs, add features

# 3. Run linting
make lint
# Runs: ruff, mypy, black, isort

# 4. Run tests
make test
# Requires PostgreSQL for integration tests

# 5. Commit with conventional message
git add .
git commit -m "feat: description of changes"
# Types: feat, fix, docs, chore, perf, refactor, test

# 6. Push to GitHub
git push origin feature/my-changes

# 7. Create Pull Request
# Go to GitHub and create PR

# 8. On merge to main:
# - Semantic version created automatically
# - GitHub release created
# - Documentation deployed
```

### Viewing Coverage

```bash
# Open HTML coverage report (macOS)
open htmlcov/index.html

# Or view in browser manually
# htmlcov/index.html
```

### Type Checking

```bash
mypy src/genew4_orm
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

- [Getting Started](https://hgnc.github.io/genew4-orm/getting-started/) - Installation and configuration
- [Configuration](https://hgnc.github.io/genew4-orm/configuration/) - Environment variables and settings
- [Models](https://hgnc.github.io/genew4-orm/models/) - Database model reference
- [Querying](https://hgnc.github.io/genew4-orm/querying/) - Query helpers and eager loading
- [API Reference](https://hgnc.github.io/genew4-orm/api-reference/) - Auto-generated API docs
- [CRUD Operations](https://hgnc.github.io/genew4-orm/crud-operations/) - Create, read, update, delete guide
- [Audit Logging](https://hgnc.github.io/genew4-orm/audit-logging/) - Automatic audit trail
- [Testing](https://hgnc.github.io/genew4-orm/testing/) - Test suite guide

## Getting Help

You can get interactive help with the documentation via the [genew4-orm MCP server](https://hgnc.gitmcp.io/genew4-orm). The MCP (Model Context Protocol) server provides AI-assisted documentation search and code examples directly within compatible tools like Claude Code.

You can also chat with the MCP server at [https://hgnc.gitmcp.io/genew4-orm/chat](https://hgnc.gitmcp.io/genew4-orm/chat) for quick questions and code examples.
