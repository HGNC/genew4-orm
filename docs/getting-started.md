# Getting Started

This guide will help you get started with genew4-orm.

## Installation

### Requirements

- Python 3.13 or higher
- PostgreSQL 12 or higher
- uv (recommended) or pip for package management

### Install with uv (Recommended)

```bash
# Create a new project
uv init

# Add genew4-orm
uv add genew4-orm
```

### Install with pip

```bash
pip install genew4-orm
```

### Install with Documentation Dependencies

```bash
# For development with documentation
uv add --dev mkdocs mkdocs-material mkdocstrings
```

## Configuration

Create a `.env` file in your project root. All variables are prefixed with
`DATABASESETTINGS_`; the `DATABASESETTINGS_PG_*` names shown here are accepted
as legacy aliases of the canonical fields:

```bash
# PostgreSQL Configuration
DATABASESETTINGS_PG_HOST=localhost
DATABASESETTINGS_PG_PORT=5432
DATABASESETTINGS_PG_NAME=genew4
DATABASESETTINGS_PG_USER=your_username
DATABASESETTINGS_PG_PASSWORD=your_password

# Connection Pool Settings (Optional)
DATABASESETTINGS_POOL_SIZE=5
DATABASESETTINGS_MAX_OVERFLOW=10
DATABASESETTINGS_POOL_TIMEOUT=30
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASESETTINGS_PG_HOST` | PostgreSQL host (alias of `DATABASESETTINGS_HOST`) | `localhost` |
| `DATABASESETTINGS_PG_PORT` | PostgreSQL port (alias of `DATABASESETTINGS_PORT`) | `5432` |
| `DATABASESETTINGS_PG_NAME` | Database name (alias of `DATABASESETTINGS_DATABASE`) | `genew4` |
| `DATABASESETTINGS_PG_USER` | Database user (alias of `DATABASESETTINGS_USERNAME`) | *(required)* |
| `DATABASESETTINGS_PG_PASSWORD` | Database password (alias of `DATABASESETTINGS_PASSWORD`) | *(required)* |
| `DATABASESETTINGS_POOL_SIZE` | Connection pool size | `5` |
| `DATABASESETTINGS_MAX_OVERFLOW` | Max overflow connections | `10` |
| `DATABASESETTINGS_POOL_TIMEOUT` | Connection pool timeout (seconds) | `30` |
| `DATABASESETTINGS_POOL_RECYCLE` | Recycle connections after N seconds | `3600` |
| `DATABASESETTINGS_POOL_PRE_PING` | Test connections before checkout | `true` |

## First Query

### Initialize the Engine

```python
from genew4_orm.config import DatabaseSettings
from genew4_orm.session import initialize_engine

# Option 1: Load from environment variables
initialize_engine()

# Option 2: Pass settings directly
settings = DatabaseSettings(
    host="localhost",
    port=5432,
    database="genew4",
    username="your_user",
    password="your_password",
)
initialize_engine(settings)
```

> The legacy `pg_host` / `pg_port` / `pg_name` / `pg_user` / `pg_password`
> keyword arguments still work as aliases of the canonical `host` / `port` /
> `database` / `username` / `password` fields.

### Create a Read-Write Session

```python
from genew4_orm.models import Gene
from genew4_orm.session import get_readwrite_session

with get_readwrite_session(user="your_name") as session:
    # Get a gene by ID
    gene = session.get(Gene, 12345)

    if gene:
        print(f"Gene: {gene.approved_symbol} - {gene.approved_name}")

        # Update the gene
        gene.approved_name = "Updated Name"
        # The session commits automatically on a clean exit.
```

### Create a Read-Only Session

```python
from sqlalchemy import select

from genew4_orm.models import Gene
from genew4_orm.session import get_readonly_session

with get_readonly_session() as session:
    # Query all approved genes
    statement = select(Gene).where(Gene.status == "Approved")
    results = session.scalars(statement).all()

    for gene in results:
        print(f"Gene: {gene.approved_symbol}")
```

### Query with Joins

```python
from sqlalchemy import select

from genew4_orm.models import Gene
from genew4_orm.utils.query_helpers import get_gene_with_groups

with get_readonly_session() as session:
    # Get genes with their associated groups eagerly loaded (no N+1 queries)
    statement = select(Gene).options(get_gene_with_groups())
    genes = session.scalars(statement).all()

    for gene in genes:
        for association in gene.gene_has_gene_groups:
            print(f"Group: {association.gene_group.name}")
```

## Getting Help

### MCP Server

You can get interactive help with the documentation via the [genew4-orm MCP server](https://hgnc.gitmcp.io/genew4-orm). The MCP (Model Context Protocol) server provides AI-assisted documentation search and code examples directly within compatible tools like Claude Code.

You can also chat with the MCP server at [https://hgnc.gitmcp.io/genew4-orm/chat](https://hgnc.gitmcp.io/genew4-orm/chat) for quick questions and code examples.

### Documentation

- [Models](models.md) - Learn about available database models
- [Querying](querying.md) - Advanced querying techniques
- [Development Workflow](development-workflow.md) - Contributing and CI/CD process
