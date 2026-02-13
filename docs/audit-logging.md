# Audit Logging

genew4-orm provides automatic audit logging for all write operations. This ensures complete traceability of data changes in the genew4 database.

## Overview

The audit logging system automatically tracks:
- **CREATE** operations - New records added
- **UPDATE** operations - Field modifications
- **DELETE** operations - Record removals

Each audit entry includes:
- **Timestamp** - When the operation occurred
- **User** - Who performed the operation
- **Operation type** - CREATE, UPDATE, or DELETE
- **Entity** - The model type that was modified
- **Entity ID** - The primary key of the affected record
- **Field changes** - Before/after values for UPDATE operations

## Audit Log Model

```python
from genew4_orm.models import AuditLog

audit = AuditLog(
    user="curator",
    operation="UPDATE",
    entity_type="Gene",
    entity_id=12345,
    field_changes={
        "approved_name": {"old": "Old Name", "new": "New Name"},
        "editor": {"old": "previous_curator", "new": "curator"},
    },
)
```

## Automatic Logging

### CREATE Operations

```python
from genew4_orm.session import get_readwrite_session
from genew4_orm.models import Gene, AuditLog

with get_readwrite_session(user="curator") as session:
    gene = Gene(
        approved_symbol="TEST1",
        approved_name="Test Gene 1",
        status="Approved",
    )
    session.add(gene)
    session.commit()

# Audit log entry automatically created:
# AuditLog(
#     user="curator",
#     operation="CREATE",
#     entity_type="Gene",
#     entity_id=<new_gene_id>,
#     field_changes={
#         "approved_symbol": {"old": None, "new": "TEST1"},
#         "approved_name": {"old": None, "new": "Test Gene 1"},
#         "status": {"old": None, "new": "Approved"},
#         ...
#     }
# )
```

### UPDATE Operations

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated Name"
    gene.editor = "curator"
    session.commit()

# Audit log entry automatically created:
# AuditLog(
#     user="curator",
#     operation="UPDATE",
#     entity_type="Gene",
#     entity_id=12345,
#     field_changes={
#         "approved_name": {"old": "Original Name", "new": "Updated Name"},
#         "editor": {"old": "previous_editor", "new": "curator"},
#     }
# )
```

### DELETE Operations

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    session.delete(gene)
    session.commit()

# Audit log entry automatically created:
# AuditLog(
#     user="curator",
#     operation="DELETE",
#     entity_type="Gene",
#     entity_id=12345,
#     field_changes={}
# )
```

## Querying Audit Logs

### Get Recent Changes

```python
from sqlmodel import select
from genew4_orm.models import AuditLog

with get_readonly_session() as session:
    # Get last 10 audit entries
    statement = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10)
    audits = session.exec(statement).all()

    for audit in audits:
        print(f"{audit.timestamp} - {audit.user} - {audit.operation} {audit.entity_type}:{audit.entity_id}")
```

### Get Changes by User

```python
with get_readonly_session() as session:
    statement = select(AuditLog).where(AuditLog.user == "curator")
    audits = session.exec(statement).all()
```

### Get Changes for Specific Entity

```python
with get_readonly_session() as session:
    statement = select(AuditLog).where(
        AuditLog.entity_type == "Gene",
        AuditLog.entity_id == 12345
    ).order_by(AuditLog.timestamp.desc())

    audits = session.exec(statement).all()

    for audit in audits:
        print(f"{audit.operation} on {audit.timestamp}")
        if audit.field_changes:
            for field, change in audit.field_changes.items():
                print(f"  {field}: {change.get('old')} -> {change.get('new')}")
```

### Get Changes by Date Range

```python
from datetime import datetime, timedelta

with get_readonly_session() as session:
    # Last 7 days
    start_date = datetime.now() - timedelta(days=7)

    statement = select(AuditLog).where(
        AuditLog.timestamp >= start_date
    ).order_by(AuditLog.timestamp.desc())

    audits = session.exec(statement).all()
```

## Audit Log Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key |
| `timestamp` | `datetime` | When the operation occurred |
| `user` | `str` | Username who performed the operation |
| `operation` | `str` | CREATE, UPDATE, or DELETE |
| `entity_type` | `str` | Model class name (e.g., "Gene", "GeneGroup") |
| `entity_id` | `int` | ID of the affected record |
| `field_changes` | `dict` | Field name -> {old, new} values |

## Session Requirements

Audit logging requires the `user` parameter when creating read-write sessions:

```python
# REQUIRED: User parameter for audit logging
with get_readwrite_session(user="username") as session:
    # All write operations are logged with this username
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated"
    session.commit()

# Read-only sessions don't require user (no write operations)
with get_readonly_session() as session:
    results = session.exec(select(Gene)).all()
```

## Implementation Details

The audit logging is implemented via SQLAlchemy event listeners in the session module:

1. **Before flush** - Detects dirty (modified) objects and pending (new) objects
2. **After flush** - Records DELETE operations
3. **Automatic commit** - Audit log entries are committed in the same transaction as the data changes

This ensures:
- **Atomicity** - Audit entries are only saved if the data operation succeeds
- **Consistency** - Every write operation has a corresponding audit trail
- **Performance** - Minimal overhead on write operations

## Best Practices

1. **Always use meaningful usernames** - Use real usernames or service account names
2. **Query audit logs regularly** - Review changes for data integrity
3. **Archive old logs** - Consider archiving audit logs periodically for performance
4. **Monitor suspicious activity** - Set up alerts for bulk DELETE operations
5. **Include audit context** - Use descriptive usernames that include the application/service

## Example: Complete Audit Workflow

```python
from genew4_orm.session import get_readwrite_session, get_readonly_session
from genew4_orm.models import Gene, AuditLog
from sqlmodel import select

# Step 1: Make changes
with get_readwrite_session(user="curator_john") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated by John"
    session.commit()

# Step 2: Review audit trail
with get_readonly_session() as session:
    statement = select(AuditLog).where(
        AuditLog.entity_type == "Gene",
        AuditLog.entity_id == 12345
    ).order_by(AuditLog.timestamp.desc())

    audits = session.exec(statement).all()

    print(f"Audit trail for Gene {12345}:")
    for audit in audits:
        print(f"  {audit.timestamp}: {audit.user} {audit.operation}")
        if audit.field_changes:
            for field, change in audit.field_changes.items():
                print(f"    {field}: {change.get('old')} -> {change.get('new')}")
```

## Troubleshooting

### Missing Audit Entries

If audit entries are not being created:

1. **Check user parameter** - Ensure `user` is passed to `get_readwrite_session()`
2. **Check session type** - Only read-write sessions create audit logs
3. **Check commit** - Audit logs are only created on successful commit

### Performance Issues

For high-volume write operations:

1. **Consider bulk operations** - Bulk operations create fewer audit entries
2. **Archive old logs** - Move old audit logs to separate storage
3. **Add indexes** - Add database indexes on frequently queried audit fields

```python
# Example: Archive old audit logs
from datetime import datetime, timedelta

cutoff_date = datetime.now() - timedelta(days=90)

with get_readwrite_session(user="archive_job") as session:
    old_logs = session.exec(
        select(AuditLog).where(AuditLog.timestamp < cutoff_date)
    ).all()

    # Export to cold storage (CSV, S3, etc.)
    # Then delete from database
    for log in old_logs:
        session.delete(log)

    session.commit()
```
