# CRUD Operations

This guide covers Create, Read, Update, and Delete operations with genew4-orm, including session management and audit logging.

## Session Management

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

### Read-Write Sessions

For operations that modify data:

```python
from genew4_orm.session import get_readwrite_session
from genew4_orm.models import Gene

with get_readwrite_session(user="your_username") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated Name"
    session.commit()
```

The `user` parameter is required for audit logging. All write operations are automatically tracked with the username and timestamp.

### Read-Only Sessions

For queries only (prevents accidental modifications):

```python
from genew4_orm.session import get_readonly_session

with get_readonly_session() as session:
    from sqlmodel import select
    results = session.exec(select(Gene)).all()
```

Read-only sessions reject `add()`, `delete()`, and `commit()` operations.

### Close All Sessions

When shutting down your application:

```python
from genew4_orm.session import close_all_sessions

close_all_sessions()
```

## Create Operations

### Create Single Record

```python
from genew4_orm.session import get_readwrite_session
from genew4_orm.models import GeneGroup

with get_readwrite_session(user="curator") as session:
    group = GeneGroup(
        name="Test Gene Family",
        abbreviation="TGF",
        status="internal",
        type="family",
        description="A test gene family",
    )
    session.add(group)
    session.commit()

    # Refresh to get generated ID
    session.refresh(group)
    print(f"Created group with ID: {group.id}")
```

### Create Multiple Records

```python
with get_readwrite_session(user="curator") as session:
    groups = [
        GeneGroup(name="Group 1", abbreviation="G1", status="internal", type="set"),
        GeneGroup(name="Group 2", abbreviation="G2", status="internal", type="set"),
    ]
    session.add_all(groups)
    session.commit()
```

### Create with Relationships

```python
from genew4_orm.models import Gene, GeneGroup, GeneHasGeneGroup

with get_readwrite_session(user="curator") as session:
    # Create gene
    gene = Gene(
        approved_symbol="TEST1",
        approved_name="Test Gene 1",
        status="Approved",
        locus_type="gene with protein product",
    )
    session.add(gene)
    session.flush()  # Get gene ID without committing

    # Create group
    group = GeneGroup(
        name="Test Group",
        abbreviation="TG",
        status="internal",
        type="set",
    )
    session.add(group)
    session.flush()

    # Create association
    association = GeneHasGeneGroup(
        gene_id=gene.id,
        gene_group_id=group.id,
        sort_order=1,
    )
    session.add(association)
    session.commit()
```

### Create Comment Linked to Gene

```python
from genew4_orm.models import Comment, GeneHasComment
from genew4_orm.enums import PublishStatus

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
    session.commit()
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
from sqlmodel import select

with get_readonly_session() as session:
    statement = select(Gene).where(Gene.status == "Approved")
    results = session.exec(statement).all()

    for gene in results:
        print(gene.approved_symbol)
```

### Select Single Record

```python
with get_readonly_session() as session:
    statement = select(Gene).where(Gene.approved_symbol == "BRCA1")
    gene = session.exec(statement).first()
```

### Select with Multiple Conditions

```python
from sqlmodel import and_, or_

with get_readonly_session() as session:
    statement = select(Gene).where(
        and_(
            Gene.status == "Approved",
            Gene.locus_type == "gene with protein product",
        )
    )
    results = session.exec(statement).all()
```

### Count Records

```python
from sqlmodel import func

with get_readonly_session() as session:
    statement = select(func.count(Gene.id))
    count = session.exec(statement).one()
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
        session.commit()
```

### Update Multiple Records

```python
from sqlmodel import select

with get_readwrite_session(user="curator") as session:
    statement = select(Gene).where(Gene.status == "Pending")
    results = session.exec(statement).all()

    for gene in results:
        gene.status = "Approved"

    session.commit()
```

### Bulk Update with execute

```python
from sqlalchemy import update

with get_readwrite_session(user="curator") as session:
    stmt = update(Gene).where(Gene.status == "Pending").values(status="Approved")
    session.execute(stmt)
    session.commit()
```

## Delete Operations

### Delete Single Record

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    if gene:
        session.delete(gene)
        session.commit()
```

### Delete Multiple Records

```python
from sqlmodel import select

with get_readwrite_session(user="curator") as session:
    statement = select(Gene).where(Gene.status == "Withdrawn")
    results = session.exec(statement).all()

    for gene in results:
        session.delete(gene)

    session.commit()
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
        session.commit()
```

## Transaction Management

### Commit Changes

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated"
    session.commit()  # Persist changes
```

### Rollback Changes

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "This will be rolled back"
    session.rollback()  # Undo changes

    # Or use context manager for automatic rollback on exception
    try:
        gene.approved_name = "Updated"
        session.commit()
    except Exception as e:
        session.rollback()
        raise
```

### Nested Transactions (Savepoints)

```python
with get_readwrite_session(user="curator") as session:
    session.begin_nested()

    try:
        # Operations that can be rolled back independently
        gene = Gene(approved_symbol="TEST", approved_name="Test")
        session.add(gene)
        session.commit()  # Commits nested transaction
    except Exception:
        session.rollback()  # Rolls back nested transaction only

    session.commit()  # Commits outer transaction
```

## Best Practices

1. **Always use context managers** (`with` statements) for automatic cleanup
2. **Specify user parameter** in read-write sessions for audit logging
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
        group = GeneGroup(name="Duplicate Name", abbreviation="DUP", status="internal", type="set")
        session.add(group)
        session.commit()
except IntegrityError as e:
    print(f"Constraint violation: {e}")
    session.rollback()
```

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
