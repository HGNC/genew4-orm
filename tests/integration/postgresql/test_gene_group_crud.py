"""GeneGroup CRUD operations integration tests with PostgreSQL.

This module tests Create, Read, Update, Delete (CRUD) operations
for GeneGroup model using actual PostgreSQL genew4 database.
"""

import pytest
from sqlalchemy import select

from genew4_orm.models import GeneGroup


@pytest.mark.usefixtures("postgres_session")
class TestGeneGroupCRUD:
    """Test GeneGroup CRUD operations with PostgreSQL."""

    def test_create_gene_group_minimal(self, postgres_session):
        """Test creating gene group with minimal required fields."""
        gene_group = GeneGroup(
            name="Test Group Minimal",
        )
        postgres_session.add(gene_group)
        postgres_session.commit()

        # Verify group was created
        postgres_session.refresh(gene_group)
        assert gene_group.id is not None
        assert gene_group.name == "Test Group Minimal"

    def test_create_gene_group_with_basic_fields(self, postgres_session):
        """Test creating gene group with basic fields."""
        gene_group = GeneGroup(
            name="Test Group Full",
            abbreviation="TGF",
            editor="test_curator",
            internal_comments="Internal curator notes",
            public_comments="Public-facing notes",
            label="Test Group Label",
            source="Test Source",
            typical_gene="GENE1",
            description="Full description of gene group",
        )
        postgres_session.add(gene_group)
        postgres_session.commit()

        postgres_session.refresh(gene_group)
        assert gene_group.id is not None
        assert gene_group.name == "Test Group Full"
        assert gene_group.abbreviation == "TGF"

    def test_read_gene_group_by_id(self, postgres_session):
        """Test reading gene group by ID."""
        gene_group = GeneGroup(
            name="Read Test Group",
            abbreviation="RTG",
        )
        postgres_session.add(gene_group)
        postgres_session.commit()

        group_id = gene_group.id

        # Read by ID
        retrieved = postgres_session.get(GeneGroup, group_id)
        assert retrieved is not None
        assert retrieved.name == "Read Test Group"
        assert retrieved.abbreviation == "RTG"

    def test_read_gene_group_by_name(self, postgres_session):
        """Test reading gene group by name."""
        import time

        ts = int(time.time() * 1000)

        gene_group = GeneGroup(
            name=f"Unique Name Test Group {ts}",
            abbreviation=f"UNQ{ts}",
        )
        postgres_session.add(gene_group)
        postgres_session.commit()

        # Read by name
        stmt = select(GeneGroup).where(GeneGroup.name == f"Unique Name Test Group {ts}")
        retrieved = postgres_session.execute(stmt).scalar_one()
        assert retrieved is not None
        assert retrieved.abbreviation == f"UNQ{ts}"

    def test_update_gene_group_basic_fields(self, postgres_session):
        """Test updating basic gene group fields."""
        gene_group = GeneGroup(
            name="Update Test Group",
            abbreviation="UTG",
        )
        postgres_session.add(gene_group)
        postgres_session.commit()

        # Update fields
        postgres_session.refresh(gene_group)
        gene_group.abbreviation = "UTG2"
        gene_group.editor = "new_editor"
        gene_group.source = "Updated Source"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(gene_group)
        assert gene_group.abbreviation == "UTG2"
        assert gene_group.editor == "new_editor"
        assert gene_group.source == "Updated Source"

    def test_delete_gene_group(self, postgres_session):
        """Test deleting a gene group."""
        gene_group = GeneGroup(
            name="Delete Test Group",
            abbreviation="DTG",
        )
        postgres_session.add(gene_group)
        postgres_session.commit()

        group_id = gene_group.id

        # Delete group
        postgres_session.delete(gene_group)
        postgres_session.commit()

        # Verify deletion
        retrieved = postgres_session.get(GeneGroup, group_id)
        assert retrieved is None

    def test_query_gene_groups_by_name_pattern(self, postgres_session):
        """Test querying gene groups by name pattern."""
        import time

        ts = int(time.time() * 1000)

        gene_group1 = GeneGroup(name=f"Wildcard Test Alpha {ts}")
        gene_group2 = GeneGroup(name=f"Wildcard Test Beta {ts}")
        gene_group3 = GeneGroup(name=f"Other Group {ts}")
        postgres_session.add_all([gene_group1, gene_group2, gene_group3])
        postgres_session.commit()

        # Query with ILIKE
        stmt = select(GeneGroup).where(GeneGroup.name.ilike(f"Wildcard Test%{ts}"))
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) == 2
        names = {g.name for g in results}
        assert names == {f"Wildcard Test Alpha {ts}", f"Wildcard Test Beta {ts}"}

    def test_query_gene_groups_order_by_name(self, postgres_session):
        """Test ordering gene groups by name."""
        import time

        ts = int(time.time() * 1000)

        gene_group1 = GeneGroup(name=f"Zebra Group {ts}")
        gene_group2 = GeneGroup(name=f"Alpha Group {ts}")
        gene_group3 = GeneGroup(name=f"Beta Group {ts}")
        postgres_session.add_all([gene_group1, gene_group2, gene_group3])
        postgres_session.commit()

        # Query with ordering
        stmt = (
            select(GeneGroup)
            .where(GeneGroup.name.in_([f"Zebra Group {ts}", f"Alpha Group {ts}", f"Beta Group {ts}"]))
            .order_by(GeneGroup.name)
        )
        results = postgres_session.execute(stmt).scalars().all()

        names = [g.name for g in results]
        assert names == [f"Alpha Group {ts}", f"Beta Group {ts}", f"Zebra Group {ts}"]

    def test_unique_name_constraint(self, postgres_session):
        """Test that gene group names can be duplicated (no unique constraint in DB)."""
        # Create first group
        gene_group1 = GeneGroup(name="Duplicate Name Group")
        postgres_session.add(gene_group1)
        postgres_session.commit()

        # Try to create second group with same name - should succeed (no unique constraint)
        gene_group2 = GeneGroup(name="Duplicate Name Group")
        postgres_session.add(gene_group2)
        postgres_session.commit()

        # Verify both groups were created with the same name
        assert gene_group1.id is not None
        assert gene_group2.id is not None
        assert gene_group1.name == gene_group2.name
