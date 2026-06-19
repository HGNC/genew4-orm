# CRUD Operations

This guide covers Create, Read, Update, and Delete operations with genew4-orm, including session management and audit logging. Queries use the SQLAlchemy 2.0 `select()` API.

## Session Management

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

### Read-Write Sessions

For operations that modify data:

```python
from genew4_orm.models import Gene
from genew4_orm.session import get_readwrite_session

with get_readwrite_session(user="your_username") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated Name"
    # The session commits automatically on a clean exit (rolls back on error).
```

The `user` keyword is captured for audit logging. All write operations are
automatically tracked with the username and timestamp.

### Read-Only Sessions

For queries only (prevents accidental modifications):

```python
from sqlalchemy import select

from genew4_orm.models import Gene
from genew4_orm.session import get_readonly_session

with get_readonly_session() as session:
    results = session.scalars(select(Gene)).all()
```

Read-only sessions raise `db_common.ReadOnlySessionError` on any commit attempt.

### Close All Sessions

When shutting down your application:

```python
from genew4_orm.session import close_all_sessions

close_all_sessions()
```

## Create Operations

### Create Single Record

```python
from genew4_orm.models import GeneGroup
from genew4_orm.session import get_readwrite_session

with get_readwrite_session(user="curator") as session:
    group = GeneGroup(
        name="Test Gene Family",
        abbreviation="TGF",
        description="A test gene family",
    )
    session.add(group)
    session.flush()  # Persist + populate generated ID within the transaction

    print(f"Created group with ID: {group.id}")
    # The session commits automatically on a clean exit.
```

### Create Multiple Records

```python
with get_readwrite_session(user="curator") as session:
    groups = [
        GeneGroup(name="Group 1", abbreviation="G1"),
        GeneGroup(name="Group 2", abbreviation="G2"),
    ]
    session.add_all(groups)
```

### Create with Relationships

```python
from genew4_orm.models import Gene, GeneGroup, GeneHasGeneGroup

with get_readwrite_session(user="curator") as session:
    # Create gene
    gene = Gene(
        hgnc_id=1100,
        approved_symbol="TEST1",
        approved_name="Test Gene 1",
        status="Approved",
        locus_type="gene with protein product",
    )
    session.add(gene)
    session.flush()  # Ensure the gene is visible for the FK

    # Create group
    group = GeneGroup(name="Test Group", abbreviation="TG")
    session.add(group)
    session.flush()

    # Create association
    association = GeneHasGeneGroup(
        gene_id=gene.hgnc_id,
        gene_group_id=group.id,
        custom_sort="A",
    )
    session.add(association)
```

### Create Comment Linked to Gene

```python
from genew4_orm.enums import PublishStatus
from genew4_orm.models import Comment, GeneHasComment
from genew4_orm.session import get_readwrite_session

with get_readwrite_session(user="curator") as session:
    # Create a comment
    comment = Comment(
        comment="This gene requires further review",
        author_id=1,
        status=PublishStatus.PENDING,
    )
    session.add(comment)
    session.flush()

    # Link comment to a gene
    gene_comment = GeneHasComment(
        comment_id=comment.id,
        hgnc_id=12345,
        editor_id=1,
    )
    session.add(gene_comment)
```

## Read Operations

### Get by ID

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    if gene:
        print(gene.approved_symbol)
```

### Select with Filters

```python
from sqlalchemy import select

from genew4_orm.session import get_readonly_session

with get_readonly_session() as session:
    statement = select(Gene).where(Gene.status == "Approved")
    results = session.scalars(statement).all()

    for gene in results:
        print(gene.approved_symbol)
```

### Select Single Record

```python
with get_readonly_session() as session:
    statement = select(Gene).where(Gene.approved_symbol == "BRCA1")
    gene = session.scalars(statement).first()
```

### Select with Multiple Conditions

```python
from sqlalchemy import and_, select

with get_readonly_session() as session:
    statement = select(Gene).where(
        and_(
            Gene.status == "Approved",
            Gene.locus_type == "gene with protein product",
        )
    )
    results = session.scalars(statement).all()
```

### Count Records

```python
from sqlalchemy import func, select

with get_readonly_session() as session:
    count = session.scalar(select(func.count(Gene.hgnc_id)))
    print(f"Total genes: {count}")
```

## Update Operations

### Update Single Record

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    if gene:
        gene.approved_name = "New Approved Name"
        gene.editor = "curator"
```

### Update Multiple Records

```python
from sqlalchemy import select

with get_readwrite_session(user="curator") as session:
    statement = select(Gene).where(Gene.status == "Pending")
    results = session.scalars(statement).all()

    for gene in results:
        gene.status = "Approved"
```

### Bulk Update with execute

```python
from sqlalchemy import update

with get_readwrite_session(user="curator") as session:
    stmt = update(Gene).where(Gene.status == "Pending").values(status="Approved")
    session.execute(stmt)
```

## Delete Operations

### Delete Single Record

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    if gene:
        session.delete(gene)
```

### Delete Multiple Records

```python
from sqlalchemy import select

with get_readwrite_session(user="curator") as session:
    statement = select(Gene).where(Gene.status == "Entry Withdrawn")
    results = session.scalars(statement).all()

    for gene in results:
        session.delete(gene)
```

### Delete with Relationships

When deleting records with relationships, CASCADE deletes are automatically handled:

```python
with get_readwrite_session(user="curator") as session:
    # Deleting a GeneGroup will cascade delete:
    # - GeneHasGeneGroup associations (CASCADE on foreign key)
    # - FamHasSpecialist associations
    # - FamHasExtResource associations
    # - FamHasCorr associations
    # - GeneGroupAlias records

    group = session.get(GeneGroup, 1)
    if group:
        session.delete(group)
```

## Transaction Management

### Commit Changes

Read-write sessions created with `get_readwrite_session()` **commit automatically**
when the `with` block exits cleanly and **roll back automatically** on any
exception. You can also commit explicitly mid-session:

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated"
    session.commit()  # Persist changes immediately
```

### Rollback Changes

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "This will be rolled back"
    session.rollback()  # Undo changes

    # Or rely on the context manager to roll back on exception:
    try:
        gene.approved_name = "Updated"
        raise RuntimeError("something went wrong")
    except Exception:
        session.rollback()
        raise
```

### Nested Transactions (Savepoints)

```python
with get_readwrite_session(user="curator") as session:
    session.begin_nested()

    try:
        # Operations that can be rolled back independently
        gene = Gene(hgnc_id=1101, approved_symbol="TEST", approved_name="Test")
        session.add(gene)
        session.commit()  # Commits nested transaction
    except Exception:
        session.rollback()  # Rolls back nested transaction only
```

## Best Practices

1. **Always use context managers** (`with` statements) for automatic commit/rollback and cleanup
2. **Pass the `user=` keyword** to read-write sessions for audit logging
3. **Use read-only sessions** for queries to prevent accidental modifications
4. **Commit frequently** to avoid long-running transactions
5. **Handle exceptions** and rollback on errors
6. **Use eager loading** for relationships to prevent N+1 queries
7. **Close sessions** when shutting down the application

## Error Handling

### Handle Record Not Found

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    if gene is None:
        print("Gene not found")
        return
```

### Handle Constraint Violations

```python
from sqlalchemy.exc import IntegrityError

try:
    with get_readwrite_session(user="curator") as session:
        group = GeneGroup(name="Duplicate Name", abbreviation="DUP")
        session.add(group)
except IntegrityError as e:
    print(f"Constraint violation: {e}")
```

> The read-write session context manager already rolls back on exception, so you
> normally do not need to call `session.rollback()` yourself in the `except` block.

### Handle Connection Errors

```python
from sqlalchemy.exc import OperationalError

try:
    with get_readwrite_session(user="curator") as session:
        # Database operations
        pass
except OperationalError as e:
    print(f"Connection error: {e}")
    # Implement retry logic or alert administrators
```
