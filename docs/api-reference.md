# API Documentation

This page provides auto-generated API documentation extracted from the source code.

## Configuration

```python
from genew4_orm.config import DatabaseSettings
```

### DatabaseSettings

::: genew4_orm.config.DatabaseSettings
    options:
      members: true
      show_if_no_docstring: true

## Session Management

### Session Functions

```python
from genew4_orm.session import (
    initialize_engine,
    get_readwrite_session,
    get_readonly_session,
    close_all_sessions,
)
```

::: genew4_orm.session.initialize_engine
    options:
      show_if_no_docstring: true

::: genew4_orm.session.get_readwrite_session
    options:
      show_if_no_docstring: true

::: genew4_orm.session.get_readonly_session
    options:
      show_if_no_docstring: true

::: genew4_orm.session.close_all_sessions
    options:
      show_if_no_docstring: true

## Query Helpers

```python
from genew4_orm.utils.query_helpers import (
    get_gene_with_groups,
    get_gene_group_with_hierarchy,
    build_gene_query,
    paginated_query,
)
```

### Eager Loading

::: genew4_orm.utils.query_helpers.get_gene_with_groups
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.get_gene_group_with_hierarchy
    options:
      show_if_no_docstring: true

### Query Builders

::: genew4_orm.utils.query_helpers.build_gene_query
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.build_gene_group_query
    options:
      show_if_no_docstring: true

### Pagination

::: genew4_orm.utils.query_helpers.paginated_query
    options:
      show_if_no_docstring: true

## Audit Logging

```python
from genew4_orm.audit import (
    get_audit_entries_for_entity,
    get_user_audit_history,
)
```

::: genew4_orm.audit.get_audit_entries_for_entity
    options:
      show_if_no_docstring: true

::: genew4_orm.audit.get_user_audit_history
    options:
      show_if_no_docstring: true

## Enums

```python
from genew4_orm.enums import (
    GeneStatus,
    GeneLocusType,
    GeneGroupStatus,
    GeneGroupType,
    PublishStatus,
)
```

::: genew4_orm.enums
    options:
      members: true
      show_if_no_docstring: true
