"""Integration tests for schema validation.

These tests verify that the ORM models connect to the actual
PostgreSQL database and basic table structures match.
"""

import pytest
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import Session as SQLAlchemySession

from genew4_orm.models import Gene


@pytest.mark.usefixtures("postgres_session")
class TestGeneSchemaValidation:
    """Verify Gene model connects to database."""

    def test_gene_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify hgnc table exists in database."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "hgnc" in inspector.get_table_names()

    def test_gene_has_columns(self, postgres_session: SQLAlchemySession) -> None:
        """Verify Gene table has columns."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        columns = inspector.get_columns("hgnc")

        # Table should have columns
        assert len(columns) > 0

    def test_gene_can_create_and_retrieve(self, postgres_session: SQLAlchemySession) -> None:
        """Verify Gene model fields work with database."""
        postgres_session.info["read_only"] = False
        postgres_session.info["user"] = "test_user"

        gene = Gene(
            approved_symbol="SCHEMA_TEST1",
            approved_name="Schema Validation Test",
            status="Approved",
            locus_type="gene with protein product",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Retrieve and verify
        retrieved = postgres_session.get(Gene, gene.hgnc_id)
        assert retrieved is not None
        assert retrieved.approved_symbol == "SCHEMA_TEST1"
        assert retrieved.approved_name == "Schema Validation Test"
        assert retrieved.status == "Approved"


@pytest.mark.usefixtures("postgres_session")
class TestGeneGroupSchemaValidation:
    """Verify GeneGroup model connects to database."""

    def test_gene_group_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify family_new table exists in database."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "family_new" in inspector.get_table_names()

    def test_gene_group_has_columns(self, postgres_session: SQLAlchemySession) -> None:
        """Verify GeneGroup table has columns."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        columns = inspector.get_columns("family_new")

        # Table should have columns
        assert len(columns) > 0


@pytest.mark.usefixtures("postgres_session")
class TestJunctionTableSchemaValidation:
    """Verify junction tables exist."""

    def test_gene_has_family_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify gene_has_family table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "gene_has_family" in inspector.get_table_names()

    def test_gene_has_family_has_columns(self, postgres_session: SQLAlchemySession) -> None:
        """Verify junction table has expected structure."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        columns = inspector.get_columns("gene_has_family")

        # Should have at least gene_id and family_id columns
        assert len(columns) >= 2


@pytest.mark.usefixtures("postgres_session")
class TestReferenceDataSchemaValidation:
    """Verify reference data tables exist."""

    def test_specialist_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify specialist table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "specialist" in inspector.get_table_names()

    def test_external_resource_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify external_resource table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "external_resource" in inspector.get_table_names()

    def test_correspondence_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify corr table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "corr" in inspector.get_table_names()

    def test_editor_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify editor table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "editor" in inspector.get_table_names()

    def test_user_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify user table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "user" in inspector.get_table_names()

    def test_reminder_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify reminder table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "reminder" in inspector.get_table_names()


@pytest.mark.usefixtures("postgres_session")
class TestGenomicMappingSchemaValidation:
    """Verify genomic mapping tables exist."""

    def test_grch38_mapping_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify coord_match_grch38 table exists."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "coord_match_grch38" in inspector.get_table_names()


@pytest.mark.usefixtures("postgres_session")
class TestAuditLogSchemaValidation:
    """Verify AuditLog model connects to database."""

    def test_audit_log_table_exists(self, postgres_session: SQLAlchemySession) -> None:
        """Verify audit_log table exists in database."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        assert "audit_log" in inspector.get_table_names()

    def test_audit_log_has_columns(self, postgres_session: SQLAlchemySession) -> None:
        """Verify AuditLog table has columns."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        columns = inspector.get_columns("audit_log")

        # Table should have columns
        assert len(columns) > 0

    def test_audit_log_has_timestamp_column(self, postgres_session: SQLAlchemySession) -> None:
        """Verify audit_log has timestamp column."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        columns = {col["name"] for col in inspector.get_columns("audit_log")}

        assert "timestamp" in columns

    def test_audit_log_has_user_column(self, postgres_session: SQLAlchemySession) -> None:
        """Verify audit_log has user column."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        columns = {col["name"] for col in inspector.get_columns("audit_log")}

        assert "user" in columns

    def test_audit_log_has_operation_column(self, postgres_session: SQLAlchemySession) -> None:
        """Verify audit_log has operation column."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        columns = {col["name"] for col in inspector.get_columns("audit_log")}

        assert "operation" in columns


@pytest.mark.usefixtures("postgres_session")
class TestCoreDatabaseTables:
    """Verify core database tables are present."""

    def test_expected_tables_exist(self, postgres_session: SQLAlchemySession) -> None:
        """Verify all expected main tables exist."""
        inspector = sqlalchemy_inspect(postgres_session.get_bind())
        db_tables = set(inspector.get_table_names())

        # Check critical tables
        critical_tables = [
            "hgnc",  # Gene
            "family_new",  # GeneGroup
            "gene_has_family",  # GeneHasGeneGroup
            "specialist",  # Specialist
            "external_resource",  # ExternalResource
            "corr",  # Correspondence
            "user",  # User
            "reminder",  # Reminder
            "audit_log",  # AuditLog
        ]

        for table in critical_tables:
            assert table in db_tables, f"Critical table {table} not found in database"

    def test_database_is_accessible(self, postgres_session: SQLAlchemySession) -> None:
        """Verify database is accessible via simple query."""
        from sqlalchemy import func, select

        from genew4_orm.models import Gene

        # Simple count query
        stmt = select(func.count(Gene.hgnc_id))
        result = postgres_session.execute(stmt).scalar()

        # Should return a number (might be 0 if empty DB)
        assert isinstance(result, int)


@pytest.mark.usefixtures("postgres_session")
class TestModelRelationships:
    """Test that model relationships work with real database."""

    def test_gene_relationships_are_accessible(self, postgres_session: SQLAlchemySession) -> None:
        """Verify Gene relationships can be accessed."""
        postgres_session.info["read_only"] = False
        postgres_session.info["user"] = "test_user"

        gene = Gene(
            approved_symbol="REL_TEST",
            approved_name="Relationship Test",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Refresh to load relationships
        postgres_session.refresh(gene)

        # Access relationship - should not error
        try:
            _ = gene.gene_has_gene_groups  # noqa: F841
        except Exception as e:
            pytest.fail(f"Failed to access gene_has_gene_groups: {e}")
