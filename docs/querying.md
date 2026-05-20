# Querying

This guide covers querying techniques with genew4-orm, including eager loading, pagination, and performance optimization.

## Basic Queries

### Select All Records

```python
from sqlmodel import Session, select
from genew4_orm.models import Gene

with Session(engine) as session:
    statement = select(Gene)
    results = session.exec(statement).all()
```

### Filter Records

```python
from sqlmodel import select

with Session(engine) as session:
    statement = select(Gene).where(Gene.status == "Approved")
    results = session.exec(statement).all()
```

### Get Single Record by ID

```python
with Session(engine) as session:
    gene = session.get(Gene, 12345)
```

## Query Helpers

genew4-orm provides helper functions in `genew4_orm.utils.query_helpers` for eager loading to prevent N+1 query problems.

### Get Gene with Groups

```python
from sqlmodel import Session, select
from genew4_orm.utils.query_helpers import get_gene_with_groups

with Session(engine) as session:
    statement = select(Gene).options(get_gene_with_groups())
    gene = session.exec(statement).first()

    # Groups are pre-loaded (no additional queries)
    for assoc in gene.gene_has_gene_groups:
        print(assoc.gene_group.name)
```

### Get GeneGroup with Hierarchy

```python
from genew4_orm.utils.query_helpers import get_gene_group_with_hierarchy

with Session(engine) as session:
    statement = select(GeneGroup).options(
        get_gene_group_with_hierarchy()
    )
    group = session.exec(statement).first()
```

### Get Comments for a Gene

```python
from sqlmodel import select
from genew4_orm.models import Gene, GeneHasComment, Comment

with Session(engine) as session:
    statement = (
        select(Comment)
        .join(GeneHasComment)
        .join(Gene)
        .where(Gene.approved_symbol == "BRCA1")
    )
    comments = session.exec(statement).all()

    for comment in comments:
        print(f"Comment: {comment.comment} (status: {comment.status})")
```

### Bulk Queries with Eager Loading

```python
from genew4_orm.utils.query_helpers import bulk_query_genes_with_groups

with Session(engine) as session:
    statement = bulk_query_genes_with_groups()
    genes = session.exec(statement).all()
```

## Advanced Queries

### ILike (Case-Insensitive Search)

```python
from sqlmodel import select

with Session(engine) as session:
    statement = select(Gene).where(
        Gene.approved_symbol.ilike("%brca%")
    )
    results = session.exec(statement).all()
```

### Multiple Conditions

```python
from sqlmodel import and_, or_

with Session(engine) as session:
    statement = select(Gene).where(
        and_(
            Gene.status == "Approved",
            Gene.locus_type == "gene with protein product",
        )
    )
    results = session.exec(statement).all()
```

### Ordering

```python
with Session(engine) as session:
    statement = select(Gene).order_by(Gene.approved_symbol)
    results = session.exec(statement).all()
```

## Pagination

### Paginated Query Helper

```python
from genew4_orm.utils.query_helpers import paginated_query

with Session(engine) as session:
    # Get page 2, 20 per page
    results, total_pages, total_count = paginated_query(
        session=session,
        statement=select(Gene),
        page=2,
        per_page=20,
    )

    print(f"Page {page} of {total_pages}, Total: {total_count}")
```

### Manual Pagination

```python
from sqlmodel import select, col

with Session(engine) as session:
    # Get total count
    count_statement = select(func.count(col(Gene.id)))
    total_count = session.exec(count_statement).one()

    # Paginate
    page = 1
    per_page = 20
    offset = (page - 1) * per_page

    statement = select(Gene).offset(offset).limit(per_page)
    results = session.exec(statement).all()
```

## Streaming Large Result Sets

### Stream Records

```python
from genew4_orm.utils.query_helpers import stream_query

with Session(engine) as session:
    statement = select(Gene)

    for gene in stream_query(session, statement, chunk_size=100):
        # Process gene in chunks
        print(gene.approved_symbol)
```

## Performance Optimization

### Eager Loading

Always use eager loading for relationships to avoid N+1 query problems:

```python
from sqlmodel import select

# BAD: N+1 queries
genes = session.exec(select(Gene)).all()
for gene in genes:
    for assoc in gene.gene_has_gene_groups:  # Additional query per gene!
        print(assoc.gene_group.name)

# GOOD: Single query with eager loading
from genew4_orm.utils.query_helpers import get_gene_with_groups

statement = select(Gene).options(get_gene_with_groups())
genes = session.exec(statement).all()
for gene in genes:
    for assoc in gene.gene_has_gene_groups:  # No additional query!
        print(assoc.gene_group.name)
```

### Select Specific Columns

```python
from sqlmodel import Session, select

with Session(engine) as session:
    # Only select needed columns
    statement = select(Gene.approved_symbol, Gene.approved_name)
    results = session.exec(statement).all()
```

### Index Usage

Ensure appropriate database indexes exist on frequently queried columns:

```python
# These queries benefit from indexes on approved_symbol and status
statement = select(Gene).where(
    Gene.approved_symbol == "BRCA1"
)

statement = select(Gene).where(
    Gene.status == "Approved"
)
```

## Raw SQL Queries

### Execute Raw SQL

```python
from sqlalchemy import text

with Session(engine) as session:
    result = session.execute(text("SELECT * FROM hgnc LIMIT 10"))
    rows = result.fetchall()
```

### Raw SQL with Parameters

```python
symbol = "BRCA1"
result = session.execute(
    text("SELECT * FROM hgnc WHERE hgnc_app_sym = :symbol"),
    {"symbol": symbol}
)
```

## Query Execution Tips

1. **Use eager loading** for relationships to prevent N+1 queries
2. **Limit result sets** with `limit()` for large queries
3. **Use specific column selection** instead of `SELECT *`
4. **Add database indexes** on frequently filtered columns
5. **Consider read replicas** for read-heavy workloads
6. **Use connection pooling** (enabled by default with pool_size=5)
