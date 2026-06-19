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
- **Field changes** - Before/after values for changed fields, stored as JSON

## Audit Log Model

Audit entries are normally created **automatically** by the audit listener
(see [Implementation Details](#implementation-details)). `field_changes` is
persisted as a JSON **string**:

```python
from genew4_orm.models import AuditLog

# Auto-generated entries store field_changes as a JSON string.
audit = AuditLog(
    user="curator",
    operation="UPDATE",
    entity_type="Gene",
    entity_id=12345,
    field_changes=json.dumps(
        {
            "approved_name": {"old": "Old Name", "new": "New Name"},
            "editor": {"old": "previous_curator", "new": "curator"},
        }
    ),
)
```

## Automatic Logging

### CREATE Operations

```python
from genew4_orm.models import Gene
from genew4_orm.session import get_readwrite_session

with get_readwrite_session(user="curator") as session:
    gene = Gene(
        hgnc_id=1100,
        approved_symbol="TEST1",
        approved_name="Test Gene 1",
        status="Approved",
    )
    session.add(gene)
    # The session commits automatically on a clean exit.

# Audit log entry automatically created:
# AuditLog(
#     user="curator",
#     operation="CREATE",
#     entity_type="Gene",
#     entity_id=0,  # 0 for INSERTs — the ID is not assigned at flush time
#     field_changes=json.dumps({
#         "approved_symbol": {"old": None, "new": "TEST1"},
#         "approved_name": {"old": None, "new": "Test Gene 1"},
#         "status": {"old": None, "new": "Approved"},
#         ...
#     }),
# )
```

> Note: for INSERT operations the `entity_id` is recorded as `0` because the
> ID is not assigned at flush time. Query audit logs by `entity_type`, `user`,
> or the `field_changes` JSON to identify a specific entity.

### UPDATE Operations

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated Name"
    gene.editor = "curator"

# Audit log entry automatically created:
# AuditLog(
#     user="curator",
#     operation="UPDATE",
#     entity_type="Gene",
#     entity_id=12345,
#     field_changes=json.dumps({
#         "approved_name": {"old": "Original Name", "new": "Updated Name"},
#         "editor": {"old": "previous_editor", "new": "curator"},
#     }),
# )
```

### DELETE Operations

```python
with get_readwrite_session(user="curator") as session:
    gene = session.get(Gene, 12345)
    session.delete(gene)

# Audit log entry automatically created:
# AuditLog(
#     user="curator",
#     operation="DELETE",
#     entity_type="Gene",
#     entity_id=12345,
#     field_changes=json.dumps({}),
# )
```

## Querying Audit Logs

`field_changes` is stored as a JSON string, so parse it with `json.loads()` when
reading it back.

### Get Recent Changes

```python
import json

from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import AuditLog

with get_readonly_session() as session:
    # Get last 10 audit entries
    statement = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10)
    audits = session.scalars(statement).all()

    for audit in audits:
        print(f"{audit.timestamp} - {audit.user} - {audit.operation} {audit.entity_type}:{audit.entity_id}")
```

### Get Changes by User

```python
with get_readonly_session() as session:
    statement = select(AuditLog).where(AuditLog.user == "curator")
    audits = session.scalars(statement).all()
```

### Get Changes for Specific Entity

```python
import json

from sqlalchemy import select

from genew4_orm import get_readonly_session
from genew4_orm.models import AuditLog

with get_readonly_session() as session:
    statement = (
        select(AuditLog)
        .where(
            AuditLog.entity_type == "Gene",
            AuditLog.entity_id == 12345,
        )
        .order_by(AuditLog.timestamp.desc())
    )
    audits = session.scalars(statement).all()

    for audit in audits:
        print(f"{audit.operation} on {audit.timestamp}")
        changes = json.loads(audit.field_changes) if audit.field_changes else {}
        for field, change in changes.items():
            print(f"  {field}: {change.get('old')} -> {change.get('new')}")
```

### Helper functions

`genew4_orm.audit` also provides convenience query helpers:

```python
from genew4_orm.audit import get_audit_entries_for_entity, get_user_audit_history
from genew4_orm import get_readonly_session

with get_readonly_session() as session:
    # All audit entries for one entity (most recent first)
    entries = get_audit_entries_for_entity(session, "Gene", 12345, limit=50)

    # All audit entries by a user (most recent first)
    history = get_user_audit_history(session, "curator", limit=50)
```

### Get Changes by Date Range

```python
from datetime import datetime, timedelta

from sqlalchemy import select

with get_readonly_session() as session:
    # Last 7 days
    start_date = datetime.now() - timedelta(days=7)

    statement = (
        select(AuditLog)
        .where(AuditLog.timestamp >= start_date)
        .order_by(AuditLog.timestamp.desc())
    )
    audits = session.scalars(statement).all()
```

## Audit Log Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key |
| `timestamp` | `datetime` | When the operation occurred |
| `user` | `str` | Username who performed the operation |
| `operation` | `str` | CREATE, UPDATE, or DELETE |
| `entity_type` | `str` | Model class name (e.g., "Gene", "GeneGroup") |
| `entity_id` | `int` | ID of the affected record (`0` for INSERTs) |
| `field_changes` | `str` | JSON string of field name -> `{old, new}` values |

## Session Requirements

Audit logging requires the `user` keyword when creating read-write sessions:

```python
# REQUIRED: user keyword for audit logging
with get_readwrite_session(user="username") as session:
    # All write operations are logged with this username
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated"

# Read-only sessions don't require user (no write operations)
with get_readonly_session() as session:
    results = session.scalars(select(Gene)).all()
```

## Implementation Details

The audit logging is implemented via SQLAlchemy event listeners in `genew4_orm.audit`:

1. **Before flush** (`audit_write_operations`) - Captures new (INSERT), dirty (UPDATE), and deleted (DELETE) objects and writes `AuditLog` rows for them.
2. **Same transaction** - Audit log rows are added to the same session, so they commit (or roll back) atomically with the data changes.

Read-only sessions are detected via `session.info["read_only"]` and skipped, and
the acting user is read from `session.info["user"]`, both populated by
`get_readonly_session()` / `get_readwrite_session()`.

This ensures:
- **Atomicity** - Audit entries are only saved if the data operation succeeds
- **Consistency** - Every write operation has a corresponding audit trail
- **Performance** - Minimal overhead on write operations

Sensitive fields (passwords, tokens, API keys, very large text) are excluded from
the recorded changes by `should_log_field()`.

## Best Practices

1. **Always use meaningful usernames** - Use real usernames or service account names
2. **Query audit logs regularly** - Review changes for data integrity
3. **Archive old logs** - Consider archiving audit logs periodically for performance
4. **Monitor suspicious activity** - Set up alerts for bulk DELETE operations
5. **Include audit context** - Use descriptive usernames that include the application/service

## Example: Complete Audit Workflow

```python
import json

from sqlalchemy import select

from genew4_orm import get_readonly_session, get_readwrite_session
from genew4_orm.models import AuditLog, Gene

# Step 1: Make changes
with get_readwrite_session(user="curator_john") as session:
    gene = session.get(Gene, 12345)
    gene.approved_name = "Updated by John"

# Step 2: Review audit trail
with get_readonly_session() as session:
    statement = (
        select(AuditLog)
        .where(
            AuditLog.entity_type == "Gene",
            AuditLog.entity_id == 12345,
        )
        .order_by(AuditLog.timestamp.desc())
    )
    audits = session.scalars(statement).all()

    print(f"Audit trail for Gene {12345}:")
    for audit in audits:
        print(f"  {audit.timestamp}: {audit.user} {audit.operation}")
        changes = json.loads(audit.field_changes) if audit.field_changes else {}
        for field, change in changes.items():
            print(f"    {field}: {change.get('old')} -> {change.get('new')}")
```

## Troubleshooting

### Missing Audit Entries

If audit entries are not being created:

1. **Check the `user` keyword** - Ensure `user=` is passed to `get_readwrite_session()`
2. **Check session type** - Only read-write sessions create audit logs (read-only sessions are skipped)
3. **Check commit** - Audit logs are only persisted when the session commits (the read-write context manager commits automatically on a clean exit)

### Performance Issues

For high-volume write operations:

1. **Consider bulk operations** - Bulk operations create fewer audit entries
2. **Archive old logs** - Move old audit logs to separate storage
3. **Add indexes** - Add database indexes on frequently queried audit fields

```python
import json
from datetime import datetime, timedelta

from sqlalchemy import select

# Example: Archive old audit logs
cutoff_date = datetime.now() - timedelta(days=90)

with get_readwrite_session(user="archive_job") as session:
    statement = select(AuditLog).where(AuditLog.timestamp < cutoff_date)
    old_logs = session.scalars(statement).all()

    # Export to cold storage (CSV, S3, etc.), then delete from the database
    for log in old_logs:
        session.delete(log)
```
