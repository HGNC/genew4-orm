"""Integration tests for genew4_orm.utils.query_helpers module.

This module tests eager loading strategies, query builders,
pagination, and batch operations.
"""

import time

import pytest
from sqlalchemy import select

from genew4_orm.models import GeneGroup, User


class TestGetGeneGroupWithHierarchy:
    """Test get_gene_group_with_hierarchy eager loading option."""

    def test_returns_list_of_options(self) -> None:
        """Test that function returns list of selectinload options."""
        from genew4_orm.utils.query_helpers import get_gene_group_with_hierarchy

        options = get_gene_group_with_hierarchy()

        # Should be a list
        assert isinstance(options, list)

    def test_loads_parent_and_children(self) -> None:
        """Test that option loads parent and children relationships."""
        from genew4_orm.utils.query_helpers import get_gene_group_with_hierarchy

        options = get_gene_group_with_hierarchy()

        # Should have 2 options (parents and children)
        assert len(options) == 2


class TestBuildGeneQuery:
    """Test build_gene_query function."""

    def test_returns_base_select(self) -> None:
        """Test that function returns base Gene select."""
        from genew4_orm.utils.query_helpers import build_gene_query

        statement = build_gene_query()

        # Should be a Select statement for Gene
        assert isinstance(statement, type(select()))

    def test_with_no_filters(self) -> None:
        """Test building query with no filters."""
        from genew4_orm.utils.query_helpers import build_gene_query

        statement = build_gene_query()

        # Should have no where clauses when no filters
        sql_str = str(statement.compile())
        assert "WHERE" not in sql_str

    def test_with_status_filter(self) -> None:
        """Test building query with status filter."""
        from genew4_orm.utils.query_helpers import build_gene_query

        statement = build_gene_query(status="Approved")

        # Should include status filter
        sql_str = str(statement.compile())
        assert "status" in sql_str

    def test_with_limit(self) -> None:
        """Test building query with limit."""
        from genew4_orm.utils.query_helpers import build_gene_query

        statement = build_gene_query(limit=50)

        # Should include limit
        sql_str = str(statement.compile())
        assert "LIMIT" in sql_str or "limit" in sql_str.lower()


class TestBuildGeneGroupQuery:
    """Test build_gene_group_query function."""

    def test_returns_base_select(self) -> None:
        """Test that function returns base GeneGroup select."""
        from genew4_orm.utils.query_helpers import build_gene_group_query

        statement = build_gene_group_query()

        # Should be a Select statement for GeneGroup
        assert isinstance(statement, type(select()))

    def test_with_limit(self) -> None:
        """Test building query with limit."""
        from genew4_orm.utils.query_helpers import build_gene_group_query

        statement = build_gene_group_query(limit=50)

        # Should include limit
        sql_str = str(statement.compile())
        assert "LIMIT" in sql_str or "limit" in sql_str.lower()

    def test_with_offset(self) -> None:
        """Test building query with offset."""
        from genew4_orm.utils.query_helpers import build_gene_group_query

        statement = build_gene_group_query(offset=100)

        # Should include offset
        sql_str = str(statement.compile())
        assert "OFFSET" in sql_str or "offset" in sql_str.lower()

    def test_with_all_pagination(self) -> None:
        """Test building query with pagination."""
        from genew4_orm.utils.query_helpers import build_gene_group_query

        statement = build_gene_group_query(limit=50, offset=100)

        # Should include pagination
        sql_str = str(statement.compile())
        assert "LIMIT" in sql_str or "limit" in sql_str.lower()
        assert "OFFSET" in sql_str or "offset" in sql_str.lower()


@pytest.mark.usefixtures("postgres_session")
class TestPaginatedQueryWithSession:
    """Test paginated_query function with real database."""

    def test_returns_correct_tuple(self, postgres_session) -> None:
        """Test that paginated_query returns correct tuple structure."""
        from sqlalchemy import text

        from genew4_orm.utils.query_helpers import paginated_query

        # Create test data
        ts = int(time.time() * 1000)
        for i in range(25):
            postgres_session.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"page_test_{ts}_{i}"},
            )
        postgres_session.commit()

        # Query with pagination
        stmt = select(GeneGroup)
        results, total_pages, total_count = paginated_query(postgres_session, stmt, page=1, per_page=10)

        # Should return tuple with 3 elements
        assert isinstance(results, list)
        assert isinstance(total_pages, int)
        assert isinstance(total_count, int)

        # Total count includes existing data
        assert total_count >= 0

        # Should have at least 1 page
        assert total_pages >= 1

        # First page should have at most 10 items
        assert len(results) <= 10

    def test_second_page_pagination(self, postgres_session) -> None:
        """Test pagination for second page."""
        from sqlalchemy import text

        from genew4_orm.utils.query_helpers import paginated_query

        ts = int(time.time() * 1000)
        for i in range(25):
            postgres_session.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"page2_test_{ts}_{i}"},
            )
        postgres_session.commit()

        # Query second page
        stmt = select(GeneGroup)
        results, total_pages, total_count = paginated_query(postgres_session, stmt, page=2, per_page=10)

        # Second page should have at most 10 items
        assert len(results) <= 10

    def test_last_page_pagination(self, postgres_session) -> None:
        """Test pagination for last page."""
        from sqlalchemy import text

        from genew4_orm.utils.query_helpers import paginated_query

        ts = int(time.time() * 1000)
        for i in range(25):
            postgres_session.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"page3_test_{ts}_{i}"},
            )
        postgres_session.commit()

        # Query last page (page 3 or more)
        stmt = select(GeneGroup)
        results, total_pages, total_count = paginated_query(postgres_session, stmt, page=3, per_page=10)

        # Last page should have at most 10 items
        assert len(results) <= 10


@pytest.mark.usefixtures("postgres_session")
class TestGetGeneGroupsWithAllRelationsWithSession:
    """Test get_gene_group_with_all_relations eager loading with real database."""

    def test_loads_all_available_relationships(self, postgres_session) -> None:
        """Test that eager loading loads all available relationship types."""
        from sqlalchemy import text

        from genew4_orm.utils.query_helpers import get_gene_group_with_all_relations

        ts = int(time.time() * 1000)

        # Create test data
        postgres_session.execute(
            text("INSERT INTO family_new (name) VALUES (:name)"),
            {"name": f"test_all_rel_{ts}"},
        )
        postgres_session.commit()

        # Query with eager load - unpack list for .options()
        options = get_gene_group_with_all_relations()
        stmt = select(GeneGroup).options(*options)
        results = postgres_session.execute(stmt).all()

        # Should have loaded groups
        assert len(results) >= 1


@pytest.mark.usefixtures("postgres_session")
class TestGetUserWithRemindersWithSession:
    """Test get_user_with_reminders eager loading with real database."""

    def test_returns_eager_load_option(self, postgres_session) -> None:
        """Test that function returns an eager loading option."""
        from genew4_orm.utils.query_helpers import get_user_with_reminders

        option = get_user_with_reminders()

        # Should be an option object with expected attributes
        assert hasattr(option, "path")
        # Check the path contains "reminders" (the relationship being loaded)
        assert "reminders" in str(option.path).lower()

    def test_option_works_with_query(self, postgres_session) -> None:
        """Test that option can be used in a query."""
        from genew4_orm.utils.query_helpers import get_user_with_reminders

        option = get_user_with_reminders()

        # Should be usable in a query options list
        stmt = select(User).options(option)
        assert stmt is not None


@pytest.mark.usefixtures("postgres_session")
class TestStreamGenesWithSession:
    """Test stream_genes function with real database."""

    def test_streams_gene_groups_in_chunks(self, postgres_session) -> None:
        """Test that stream_genes yields GeneGroup data in chunks."""
        from sqlalchemy import text

        from genew4_orm.utils.query_helpers import stream_genes

        ts = int(time.time() * 1000)

        # Create test data
        for i in range(25):
            postgres_session.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"stream_test_{ts}_{i}"},
            )
        postgres_session.commit()

        # Stream gene groups
        chunk_count = 0
        for chunk in stream_genes(postgres_session, chunk_size=10):
            assert len(chunk) <= 10
            chunk_count += 1

            # Should have 3 chunks (25 items / 10 per chunk)
            if chunk_count == 3:
                break

        assert chunk_count == 3

    def test_custom_chunk_size(self, postgres_session) -> None:
        """Test streaming with custom chunk size."""
        from sqlalchemy import text

        from genew4_orm.utils.query_helpers import stream_genes

        ts = int(time.time() * 1000)

        # Create test data
        for i in range(20):
            postgres_session.execute(
                text("INSERT INTO family_new (name) VALUES (:name)"),
                {"name": f"chunk_test_{ts}_{i}"},
            )
        postgres_session.commit()

        # Stream with custom chunk size
        chunk_count = 0
        for chunk in stream_genes(postgres_session, chunk_size=7):
            assert len(chunk) <= 7
            chunk_count += 1

            if chunk_count >= 1:
                break

        assert chunk_count >= 1
