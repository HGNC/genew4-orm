# Getting Started

This guide will help you get started with genew4-orm.

## Installation

### Requirements

- Python 3.11 or higher
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
pip install genew4orm
```

### Install with Documentation Dependencies

```bash
# For development with documentation
uv add --dev mkdocs mkdocs-material mkdocstrings
```

## Configuration

Create a `.env` file in your project root:

```bash
# PostgreSQL Configuration
DATABASESETTINGS_PG_HOST=localhost
DATABASESETTINGS_PG_PORT=5432
DATABASESETTINGS_PG_NAME=genew4
DATABASESETTINGS_PG_USER=your_username
DATABASESETTINGS_PG_PASSWORD=your_password
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASESETTINGS_PG_HOST` | PostgreSQL host | `localhost` |
| `DATABASESETTINGS_PG_PORT` | PostgreSQL port | `5432` |
| `DATABASESETTINGS_PG_NAME` | Database name | `genew4` |
| `DATABASESETTINGS_PG_USER` | Database user | (required) |
| `DATABASESETTINGS_PG_PASSWORD` | Database password | (required) |
| `DATABASESETTINGS_POOL_SIZE` | Connection pool size | `5` |
| `DATABASESETTINGS_MAX_OVERFLOW` | Max overflow connections | `10` |

## First Query

### Initialize the Engine

```python
from genew4_orm.session import initialize_engine
from genew4_orm.config import DatabaseSettings

# Option 1: Load from environment variables
initialize_engine()

# Option 2: Pass settings directly
settings = DatabaseSettings(
    pg_host="localhost",
    pg_port=5432,
    pg_name="genew4",
    pg_user="your_user",
    pg_password="your_password",
)
initialize_engine(settings)
```

### Create a Read-Write Session

```python
from genew4_orm.session import get_readwrite_session
from genew4_orm.models import Gene

with get_readwrite_session(user="your_name") as session:
    # Get a gene by ID
    gene = session.get(Gene, 12345)

    if gene:
        print(f"Gene: {gene.approved_symbol} - {gene.approved_name}")

        # Update the gene
        gene.approved_name = "Updated Name"
        session.commit()
```

### Create a Read-Only Session

```python
from genew4_orm.session import get_readonly_session

with get_readonly_session() as session:
    # Query all approved genes
    from sqlmodel import select

    statement = select(Gene).where(Gene.status == "Approved")
    results = session.exec(statement).all()

    for gene in results:
        print(f"Gene: {gene.approved_symbol}")
```

### Query with Joins

```python
from genew4_orm.utils.query_helpers import get_gene_with_groups

with get_readwrite_session(user="your_name") as session:
    # Get a gene with its associated groups (eager loading)
    statement = select(Gene).options(get_gene_with_groups())

    gene = session.exec(statement).first()

    if gene:
        for association in gene.gene_has_gene_groups:
            print(f"Group: {association.gene_group.name}")
```

## Next Steps

- [Models](models.md) - Learn about available database models
- [Querying](querying.md) - Advanced querying techniques
- [Development Workflow](development-workflow.md) - Contributing and CI/CD process
