"""Query helper functions for common database operations.

This module provides optimized query functions with eager loading to prevent
N+1 query problems. Use these functions for common query patterns.
"""

from collections.abc import Iterator
from typing import Any

# Import SQLAlchemy components first
from sqlalchemy import Select as _Select
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

# Then import models to avoid circular dependency
# The models package imports these modules during initialization
from genew4_orm.models import Gene, GeneGroup, GeneHasGeneGroup, User

# Type alias for SQLAlchemy Select
Select = _Select[Any]


def get_gene_with_groups() -> Any:
    """Eager loading option for Gene with gene groups.

    Uses selectinload for efficient loading of the gene_has_gene_groups
    relationship and related gene_group objects.

    This generates 3 queries total:
    1. Query for genes
    2. Query for gene_has_gene_groups (using IN clause)
    3. Query for gene_groups (using IN clause)

    Returns:
        SQLAlchemy eager loading option for use with select().options()

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from sqlmodel import select
        >>> from genew4_orm.utils.query_helpers import get_gene_with_groups
        >>> with get_readonly_session() as session:
        ...     genes = session.exec(
        ...         select(Gene).options(get_gene_with_groups())
        ...     ).all()
        ...     for gene in genes:
        ...         print(f"{gene.approved_symbol}: {len(gene.gene_has_gene_groups)} groups")
    """
    return selectinload(Gene.gene_has_gene_groups).selectinload(  # type: ignore[arg-type]
        GeneHasGeneGroup.gene_group  # type: ignore[arg-type]
    )


def get_gene_group_with_hierarchy() -> Any:
    """Eager loading option for GeneGroup with parent/child hierarchy.

    Uses selectinload for hierarchy closure relationships.
    This loads ancestor and descendant relationships via HierarchyClosure.

    Returns:
        SQLAlchemy eager loading option for use with select().options()

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from sqlmodel import select
        >>> from genew4_orm.utils.query_helpers import get_gene_group_with_hierarchy
        >>> with get_readonly_session() as session:
        ...     groups = session.exec(
        ...         select(GeneGroup).options(get_gene_group_with_hierarchy())
        ...     ).all()
        ...     for group in groups:
        ...         print(
        ...             f"{group.name}: "
        ...             f"{len(group.parent_hierarchy_closures)} parent closures"
        ...         )
    """
    return [
        selectinload(GeneGroup.parent_hierarchy_closures),  # type: ignore[arg-type]
        selectinload(GeneGroup.child_hierarchy_closures),  # type: ignore[arg-type]
    ]


def get_gene_group_with_all_relations() -> Any:
    """Eager loading option for GeneGroup with all available relationships.

    Loads gene groups with genes, aliases, parent_hierarchy_closures,
    and child_hierarchy_closures. Note: specialists, external resources,
    and correspondences are accessed via junction tables, not direct relationships.

    Returns:
        SQLAlchemy eager loading option for use with select().options()

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from sqlmodel import select
        >>> from genew4_orm.utils.query_helpers import get_gene_group_with_all_relations
        >>> with get_readonly_session() as session:
        ...     groups = session.exec(
        ...         select(GeneGroup).options(get_gene_group_with_all_relations())
        ...         .limit(10)
        ...     ).all()
        ...     for group in groups:
        ...         print(f"Group {group.name} has {len(group.gene_group_has_genes)} genes")
    """
    # Note: Return as list for compatibility with .options()
    # Each selectinload targets a relationship property
    return [
        selectinload(GeneGroup.gene_group_has_genes),  # type: ignore[arg-type]
        selectinload(GeneGroup.aliases),  # type: ignore[arg-type]
        selectinload(GeneGroup.parent_hierarchy_closures),  # type: ignore[arg-type]
        selectinload(GeneGroup.child_hierarchy_closures),  # type: ignore[arg-type]
    ]


def get_user_with_reminders() -> Any:
    """Eager loading option for User with reminders.

    Uses selectinload for the one-to-many user->reminders relationship.

    Returns:
        SQLAlchemy eager loading option for use with select().options()

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from sqlmodel import select
        >>> from genew4_orm.utils.query_helpers import get_user_with_reminders
        >>> with get_readonly_session() as session:
        ...     users = session.exec(
        ...         select(User).options(get_user_with_reminders())
        ...     ).all()
        ...     for user in users:
        ...         print(f"{user.display_name}: {len(user.reminders)} reminders")
    """
    return selectinload(User.reminders)  # type: ignore[arg-type]


# Query builder functions


def build_gene_query(
    *,
    status: str | None = None,
    locus_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Select:
    """Build a Gene query with optional filters and pagination.

    Args:
        status: Optional gene status filter.
        locus_type: Optional locus type filter.
        limit: Maximum number of results to return.
        offset: Number of results to skip.

    Returns:
        A Select statement ready for execution.

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from genew4_orm.utils.query_helpers import build_gene_query
        >>> with get_readonly_session() as session:
        ...     genes = session.exec(
        ...         build_gene_query(status="Approved", limit=10)
        ...     ).all()
        ...     for gene in genes:
        ...         print(f"Gene: {gene.approved_symbol}")
    """
    statement = select(Gene)

    if status is not None:
        statement = statement.where(Gene.status == status)  # type: ignore[arg-type]

    if locus_type is not None:
        statement = statement.where(Gene.locus_type == locus_type)  # type: ignore[arg-type]

    statement = statement.offset(offset).limit(limit)
    return statement


def build_gene_group_query(
    *,
    group_status: str | None = None,
    group_type: str | None = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Select:
    """Build a GeneGroup query with optional filters and pagination.

    Args:
        group_status: Optional gene group status filter.
        group_type: Optional gene group type filter.
        search: Optional search string for name/abbreviation.
        limit: Maximum number of results to return.
        offset: Number of results to skip.

    Returns:
        A Select statement ready for execution.

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from genew4_orm.utils.query_helpers import build_gene_group_query
        >>> with get_readonly_session() as session:
        ...     groups = session.exec(
        ...         build_gene_group_query(search="kinase", limit=10)
        ...     ).all()
        ...     for group in groups:
        ...         print(f"Group: {group.name}")
    """
    statement = select(GeneGroup)

    if group_status is not None:
        statement = statement.where(GeneGroup.name == group_status)

    if group_type is not None:
        statement = statement.where(GeneGroup.type == group_type)

    if search is not None:
        search_pattern = f"%{search}%"
        # Use or_() for combining conditions with type: ignore
        from sqlalchemy import or_
        # name is not nullable, abbreviation is nullable
        statement = statement.where(
            or_(
                GeneGroup.name.ilike(search_pattern),  # type: ignore[attr-defined]
                # Coalesce abbreviation to empty string for ilike comparison
                GeneGroup.abbreviation.ilike(search_pattern),  # type: ignore[union-attr]
            )
        )

    statement = statement.offset(offset).limit(limit)
    return statement


def paginated_query(
    session: Session,
    statement: Select,
    page: int,
    per_page: int = 100,
) -> tuple[list[Any], int, int]:
    """Execute a paginated query and return results with pagination info.

    Args:
        session: The SQLAlchemy session.
        statement: The Select statement to execute.
        page: Page number (1-indexed).
        per_page: Number of results per page.

    Returns:
        Tuple of (results, total_pages, total_count).

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from sqlmodel import select, Gene
        >>> from genew4_orm.utils.query_helpers import paginated_query
        >>> with get_readonly_session() as session:
        ...     statement = select(Gene)
        ...     genes, total_pages, total_count = paginated_query(
        ...         session, statement, page=1, per_page=50
        ...     )
        ...     print(f"Showing {len(genes)} of {total_count} genes (page 1 of {total_pages})")
    """
    # Get total count
    total_count = len(list(session.execute(statement).all()))  # type: ignore[attr-defined]

    # Calculate pagination
    total_pages = (total_count + per_page - 1) // per_page
    offset = (page - 1) * per_page

    # Execute paginated query
    results = session.execute(statement.offset(offset).limit(per_page)).all()  # type: ignore[attr-defined]

    return results, total_pages, total_count


# Batch query functions


def get_genes_by_ids(
    session: Session,
    gene_ids: list[int],
    *,
    eager_load: bool = False,
) -> list[Gene]:
    """Get multiple genes by their IDs in a single query.

    Args:
        session: The SQLAlchemy session.
        gene_ids: List of gene IDs to fetch.
        eager_load: If True, eagerly load gene groups.

    Returns:
        List of Gene objects.

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from genew4_orm.utils.query_helpers import get_genes_by_ids
        >>> with get_readonly_session() as session:
        ...     genes = get_genes_by_ids(session, [12345, 67890], eager_load=True)
    """
    statement = select(Gene).where(Gene.hgnc_id.in_(gene_ids))  # type: ignore[union-attr]

    if eager_load:
        statement = statement.options(get_gene_with_groups())

    return list(session.execute(statement))  # type: ignore[attr-defined]


def get_gene_groups_by_ids(
    session: Session,
    group_ids: list[int],
    *,
    eager_load: bool = False,
) -> list[GeneGroup]:
    """Get multiple gene groups by their IDs in a single query.

    Args:
        session: The SQLAlchemy session.
        group_ids: List of gene group IDs to fetch.
        eager_load: If True, eagerly load all relations.

    Returns:
        List of GeneGroup objects.

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from genew4_orm.utils.query_helpers import get_gene_groups_by_ids
        >>> with get_readonly_session() as session:
        ...     groups = get_gene_groups_by_ids(session, [1, 2, 3], eager_load=True)
    """
    statement = select(GeneGroup).where(GeneGroup.id.in_(group_ids))  # type: ignore[union-attr]

    if eager_load:
        statement = statement.options(get_gene_group_with_all_relations())

    return list(session.execute(statement))  # type: ignore[attr-defined]


# Stream query functions


def stream_genes(
    session: Session,
    *,
    chunk_size: int = 1000,
    status: str | None = None,
) -> Iterator[list[GeneGroup]]:
    """Stream gene groups in chunks to process large datasets efficiently.

    Args:
        session: The SQLAlchemy session.
        chunk_size: Number of genes to fetch per chunk.
        status: Optional status filter.

    Yields:
        Lists of GeneGroup objects.

    Example:
        >>> from genew4_orm import get_readonly_session
        >>> from genew4_orm.utils.query_helpers import stream_genes
        >>> with get_readonly_session() as session:
        ...     for chunk in stream_genes(session, chunk_size=1000):
        ...         for group in chunk:
        ...             process_group(group)
    """
    offset = 0

    while True:
        statement = select(GeneGroup).offset(offset).limit(chunk_size)

        if status is not None:
            # Filter by name prefix as proxy for status
            statement = statement.where(GeneGroup.name.like(f"{status}%"))

        chunk = list(session.execute(statement))  # type: ignore[attr-defined]

        if not chunk:
            break

        yield chunk

        offset += chunk_size
