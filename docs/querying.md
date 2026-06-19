# Querying

This guide covers querying techniques with genew4-orm, including eager loading, pagination, and performance optimization. Queries use the [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) `select()` API.

## Basic Queries

### Select All Records

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    statement = select(Gene)
    results = session.scalars(statement).all()
```

### Filter Records

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    statement = select(Gene).where(Gene.status == "Approved")
    results = session.scalars(statement).all()
```

### Get Single Record by ID

```python
from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    gene = session.get(Gene, 12345)
```

## Query Helpers

genew4-orm provides helper functions in `genew4_orm.utils.query_helpers` for eager loading to prevent N+1 query problems.

### Get Gene with Groups

`get_gene_with_groups()` returns a single (chained) loader option, so pass it
directly to `.options()`:

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.utils.query_helpers import get_gene_with_groups

with get_readonly_session() as session:
    statement = select(Gene).options(get_gene_with_groups())
    genes = session.scalars(statement).all()

    # Groups are pre-loaded (no additional queries)
    for gene in genes:
        for assoc in gene.gene_has_gene_groups:
            print(assoc.gene_group.name)
```

### Get GeneGroup with Hierarchy

`get_gene_group_with_hierarchy()` returns a **list** of loader options, so splat
it into `.options()` with `*`:

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import GeneGroup
from genew4_orm.utils.query_helpers import get_gene_group_with_hierarchy

with get_readonly_session() as session:
    statement = select(GeneGroup).options(*get_gene_group_with_hierarchy())
    groups = session.scalars(statement).all()
```

`get_gene_group_with_all_relations()` likewise returns a list — splat it the same
way: `.options(*get_gene_group_with_all_relations())`.

### Get Comments for a Gene

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Comment, Gene, GeneHasComment

with get_readonly_session() as session:
    statement = (
        select(Comment)
        .join(GeneHasComment)
        .join(Gene)
        .where(Gene.approved_symbol == "BRCA1")
    )
    comments = session.scalars(statement).all()

    for comment in comments:
        print(f"Comment: {comment.comment} (status: {comment.status})")
```

### Bulk Fetch Genes with Eager Loading

```python
from genew4_orm import get_readonly_session
from genew4_orm.utils.query_helpers import get_genes_by_ids

with get_readonly_session() as session:
    genes = get_genes_by_ids(session, [12345, 67890], eager_load=True)
```

Use `get_gene_groups_by_ids(session, [...], eager_load=True)` for the equivalent
gene-group helper.

## Advanced Queries

### ILike (Case-Insensitive Search)

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    statement = select(Gene).where(Gene.approved_symbol.ilike("%brca%"))
    results = session.scalars(statement).all()
```

### Multiple Conditions

```python
from sqlalchemy import and_, or_, select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    statement = select(Gene).where(
        and_(
            Gene.status == "Approved",
            Gene.locus_type == "gene with protein product",
        )
    )
    results = session.scalars(statement).all()
```

### Ordering

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    statement = select(Gene).order_by(Gene.approved_symbol)
    results = session.scalars(statement).all()
```

## Pagination

### Paginated Query Helper

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene
from genew4_orm.utils.query_helpers import paginated_query

with get_readonly_session() as session:
    # Get page 2, 20 per page
    results, total_pages, total_count = paginated_query(
        session=session,
        statement=select(Gene),
        page=2,
        per_page=20,
    )

    print(f"Page 2 of {total_pages}, Total: {total_count}")
```

### Manual Pagination

```python
from sqlalchemy import func, select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    # Get total count
    total_count = session.scalar(select(func.count(Gene.hgnc_id)))

    # Paginate
    page = 1
    per_page = 20
    offset = (page - 1) * per_page

    statement = select(Gene).offset(offset).limit(per_page)
    results = session.scalars(statement).all()
```

## Streaming Large Result Sets

### Stream Records

`stream_genes()` yields lists (chunks) of records so you can process large
datasets without loading everything into memory:

```python
from genew4_orm import get_readonly_session
from genew4_orm.models import GeneGroup
from genew4_orm.utils.query_helpers import stream_genes

with get_readonly_session() as session:
    # Note: despite the name, stream_genes() currently yields GeneGroup chunks.
    for chunk in stream_genes(session, chunk_size=1000):
        for group in chunk:
            print(group.name)
```

## Performance Optimization

### Eager Loading

Always use eager loading for relationships to avoid N+1 query problems:

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene
from genew4_orm.utils.query_helpers import get_gene_with_groups

# BAD: N+1 queries
with get_readonly_session() as session:
    genes = session.scalars(select(Gene)).all()
    for gene in genes:
        for assoc in gene.gene_has_gene_groups:  # Additional query per gene!
            print(assoc.gene_group.name)

# GOOD: Single query with eager loading
with get_readonly_session() as session:
    statement = select(Gene).options(get_gene_with_groups())
    genes = session.scalars(statement).all()
    for gene in genes:
        for assoc in gene.gene_has_gene_groups:  # No additional query!
            print(assoc.gene_group.name)
```

### Select Specific Columns

```python
from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import Gene

with get_readonly_session() as session:
    # Only select needed columns (returns Row tuples)
    statement = select(Gene.approved_symbol, Gene.approved_name)
    results = session.execute(statement).all()
```

### Index Usage

Ensure appropriate database indexes exist on frequently queried columns:

```python
# These queries benefit from indexes on approved_symbol and status
statement = select(Gene).where(Gene.approved_symbol == "BRCA1")

statement = select(Gene).where(Gene.status == "Approved")
```

## Raw SQL Queries

### Execute Raw SQL

```python
from sqlalchemy import text

from genew4_orm import get_readonly_session

with get_readonly_session() as session:
    result = session.execute(text("SELECT * FROM hgnc LIMIT 10"))
    rows = result.fetchall()
```

### Raw SQL with Parameters

```python
symbol = "BRCA1"
result = session.execute(
    text("SELECT * FROM hgnc WHERE hgnc_app_sym = :symbol"),
    {"symbol": symbol},
)
```

## Query Execution Tips

1. **Use eager loading** for relationships to prevent N+1 queries
2. **Limit result sets** with `limit()` for large queries
3. **Use specific column selection** instead of `SELECT *`
4. **Add database indexes** on frequently filtered columns
5. **Consider read replicas** for read-heavy workloads
6. **Use connection pooling** (enabled by default with `pool_size=5`)
