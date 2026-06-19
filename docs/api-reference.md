# API Documentation

This page provides auto-generated API documentation extracted from the source
code via [mkdocstrings](https://mkdocstrings.github.io/). The code examples in
this library use the [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
`select()` API.

## Configuration

```python
from genew4_orm.config import DatabaseSettings
```

`DatabaseSettings` is the backwards-compatible alias for
`Genew4DatabaseSettings`, which subclasses `db_common.DatabaseSettings`.

::: genew4_orm.config.DatabaseSettings
    options:
      members: true
      show_if_no_docstring: true

## Session Management

```python
from genew4_orm.session import (
    SessionError,
    ReadOnlySessionError,
    close_all_sessions,
    get_engine,
    get_readonly_session,
    get_readwrite_session,
    get_settings,
    initialize_engine,
    refresh_engine,
)
```

### Engine and settings

::: genew4_orm.session.initialize_engine
    options:
      show_if_no_docstring: true

::: genew4_orm.session.get_engine
    options:
      show_if_no_docstring: true

::: genew4_orm.session.get_settings
    options:
      show_if_no_docstring: true

::: genew4_orm.session.refresh_engine
    options:
      show_if_no_docstring: true

### Sessions

::: genew4_orm.session.get_readwrite_session
    options:
      show_if_no_docstring: true

::: genew4_orm.session.get_readonly_session
    options:
      show_if_no_docstring: true

### Cleanup and exceptions

::: genew4_orm.session.close_all_sessions
    options:
      show_if_no_docstring: true

::: genew4_orm.session.SessionError
    options:
      show_if_no_docstring: true

::: genew4_orm.session.ReadOnlySessionError
    options:
      show_if_no_docstring: true

## Query Helpers

```python
from genew4_orm.utils.query_helpers import (
    build_gene_group_query,
    build_gene_query,
    get_gene_group_with_all_relations,
    get_gene_group_with_hierarchy,
    get_gene_groups_by_ids,
    get_gene_with_groups,
    get_genes_by_ids,
    get_user_with_reminders,
    paginated_query,
    stream_genes,
)
```

### Eager loading

::: genew4_orm.utils.query_helpers.get_gene_with_groups
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.get_gene_group_with_hierarchy
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.get_gene_group_with_all_relations
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.get_user_with_reminders
    options:
      show_if_no_docstring: true

### Query builders

::: genew4_orm.utils.query_helpers.build_gene_query
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.build_gene_group_query
    options:
      show_if_no_docstring: true

### Pagination, bulk fetch, and streaming

::: genew4_orm.utils.query_helpers.paginated_query
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.get_genes_by_ids
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.get_gene_groups_by_ids
    options:
      show_if_no_docstring: true

::: genew4_orm.utils.query_helpers.stream_genes
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
    CytobandSourceType,
    GeneGroupStatus,
    GeneGroupType,
    GeneLocusType,
    GeneStatus,
    Grch38MarkType,
    Grch38SourceType,
    PublishStatus,
    enum_field,
)
```

::: genew4_orm.enums
    options:
      members: true
      show_if_no_docstring: true
