# genew4-orm

Python ORM for the genew4 PostgreSQL database.

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

## Documentation

Full documentation coming soon.

## Features

- Type-safe models with Pydantic validation
- Read-only by default (safe mode)
- Full CRUD when needed
- Audit logging for all writes
- Comprehensive test suite
