# genew4-orm - Python ORM for the genew4 PostgreSQL database

genew4-orm is a Python Object-Relational Mapping (ORM) library for the Gene Nomenclature (genew4) PostgreSQL database. It provides type-safe database models, session management, and automatic audit logging.

## Features

- **Type-Safe Models**: Built with [SQLModel](https://sqlmodel.tiangolo.com/) and Pydantic for full type checking
- **PostgreSQL Support**: Optimized for PostgreSQL with psycopg driver
- **Audit Logging**: Automatic tracking of all write operations
- **Read-Only Sessions**: Built-in protection against accidental modifications
- **Query Helpers**: Eager loading utilities to prevent N+1 queries
- **Database Migrations**: Alembic integration for schema management
- **CI/CD Pipeline**: Automated testing, releases, and documentation deployment via GitHub Actions

## Installation

```bash
# Using uv (recommended)
uv add genew4-orm

# Or using pip
pip install genew4-orm
```

## Quick Start

```python
from genew4_orm.session import initialize_engine, get_readwrite_session
from genew4_orm.models import Gene

# Initialize database connection
initialize_engine()

# Create a session
with get_readwrite_session(user="your_user") as session:
    # Query a gene
    gene = session.get(Gene, 12345)
    print(gene.approved_symbol, gene.approved_name)
```

## Documentation

- [Getting Started](getting-started.md) - Installation and configuration
- [Configuration](configuration.md) - Environment variables and settings
- [Models](models.md) - Database model reference
- [Querying](querying.md) - Query helpers and eager loading
- [API Reference](api-reference.md) - Auto-generated API docs
- [CRUD Operations](crud-operations.md) - Create, read, update, delete guide
- [Audit Logging](audit-logging.md) - Automatic audit trail
- [Testing](testing.md) - Test suite guide
- [Development Workflow](development-workflow.md) - Contributing and CI/CD

## Getting Help

You can get interactive help with the documentation via the [genew4-orm MCP server](https://hgnc.gitmcp.io/genew4-orm). The MCP (Model Context Protocol) server provides AI-assisted documentation search and code examples directly within compatible tools like Claude Code.

You can also chat with the MCP server at [https://hgnc.gitmcp.io/hgnc/genew4-orm/chat](https://hgnc.gitmcp.io/hgnc/genew4-orm/chat) for quick questions and code examples.

## License

MIT License - see LICENSE file for details.
