"""Integration tests for Specialist model with PostgreSQL.

This module tests Specialist CRUD operations with real database connections,
including testing relationships with GeneGroup.
"""

import time

import pytest
from sqlalchemy import select, text

from genew4_orm.models.specialist import Specialist
from genew4_orm.models.gene_group import GeneGroup
from genew4_orm.models.fam_has_specialist import FamHasSpecialist


@pytest.mark.usefixtures("postgres_session")
class TestSpecialistCRUD:
    """Test Specialist CRUD operations with PostgreSQL."""

    def test_create_specialist_minimal(self, postgres_session):
        """Test creating specialist with minimal required fields."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"Test Specialist {ts}",
            address=f"123 Test Street, Test City {ts}",
        )
        postgres_session.add(specialist)
        postgres_session.commit()
        postgres_session.refresh(specialist)

        assert specialist.id is not None
        assert specialist.name == f"Test Specialist {ts}"
        assert specialist.address == f"123 Test Street, Test City {ts}"

    def test_create_specialist_with_all_fields(self, postgres_session):
        """Test creating specialist with all fields."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"Complete Specialist {ts}",
            address=f"456 Complete Ave, Full City {ts}, TC 12345",
            url="https://example.com/specialist",
        )
        postgres_session.add(specialist)
        postgres_session.commit()
        postgres_session.refresh(specialist)

        assert specialist.name == f"Complete Specialist {ts}"
        assert specialist.address == f"456 Complete Ave, Full City {ts}, TC 12345"
        assert specialist.url == "https://example.com/specialist"

    def test_read_specialist_by_id(self, postgres_session):
        """Test reading specialist by ID."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"Read Test Specialist {ts}",
            address=f"789 Read Blvd {ts}",
        )
        postgres_session.add(specialist)
        postgres_session.commit()
        specialist_id = specialist.id

        # Read by ID
        retrieved_specialist = postgres_session.get(Specialist, specialist_id)

        assert retrieved_specialist is not None
        assert retrieved_specialist.name == f"Read Test Specialist {ts}"
        assert retrieved_specialist.address == f"789 Read Blvd {ts}"

    def test_update_specialist_fields(self, postgres_session):
        """Test updating specialist fields."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"Original Name {ts}",
            address=f"Original Address {ts}",
            url="https://example.com/old",
        )
        postgres_session.add(specialist)
        postgres_session.commit()

        # Update fields
        specialist.name = f"Updated Name {ts}"
        specialist.address = f"Updated Address {ts}"
        specialist.url = "https://example.com/new"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(specialist)
        assert specialist.name == f"Updated Name {ts}"
        assert specialist.address == f"Updated Address {ts}"
        assert specialist.url == "https://example.com/new"

    def test_update_specialist_url_to_none(self, postgres_session):
        """Test updating specialist URL to None."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"URL Test Specialist {ts}",
            address=f"Test Address {ts}",
            url="https://example.com/test",
        )
        postgres_session.add(specialist)
        postgres_session.commit()

        # Set URL to None
        specialist.url = None
        postgres_session.commit()

        postgres_session.refresh(specialist)
        assert specialist.url is None

    def test_delete_specialist(self, postgres_session):
        """Test deleting specialist."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"Delete Test Specialist {ts}",
            address=f"Delete Address {ts}",
        )
        postgres_session.add(specialist)
        postgres_session.commit()
        specialist_id = specialist.id

        # Delete specialist
        postgres_session.delete(specialist)
        postgres_session.commit()

        # Verify deletion
        deleted_specialist = postgres_session.get(Specialist, specialist_id)
        assert deleted_specialist is None

    def test_query_specialists_by_name_pattern(self, postgres_session):
        """Test querying specialists by name pattern."""
        ts = int(time.time() * 1000)
        # Create multiple specialists
        for i in range(3):
            specialist = Specialist(
                name=f"Specialist Pattern {ts}-{i}",
                address=f"{i} Test Street {ts}",
            )
            postgres_session.add(specialist)
        postgres_session.commit()

        # Query with wildcard - use pattern that matches our test data only
        stmt = select(Specialist).where(
            Specialist.name.like(f"Specialist Pattern {ts}-%")
        ).order_by(Specialist.name)
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) == 3

    def test_query_specialists_with_url(self, postgres_session):
        """Test querying specialists that have URLs."""
        ts = int(time.time() * 1000)
        # Create specialists with and without URLs
        specialist1 = Specialist(
            name=f"With URL {ts}",
            address=f"Address 1 {ts}",
            url="https://example.com/with-url",
        )
        specialist2 = Specialist(
            name=f"Without URL {ts}",
            address=f"Address 2 {ts}",
        )
        postgres_session.add_all([specialist1, specialist2])
        postgres_session.commit()

        # Query specialists with URLs - filter by our test data
        stmt = select(Specialist).where(
            Specialist.url.isnot(None),
            Specialist.name.like(f"%{ts}%")
        )
        with_url = postgres_session.execute(stmt).scalars().all()

        names = {s.name for s in with_url}
        assert f"With URL {ts}" in names
        assert f"Without URL {ts}" not in names


@pytest.mark.usefixtures("postgres_session")
class TestSpecialistGeneGroupRelationship:
    """Test Specialist relationship with GeneGroup via FamHasSpecialist."""

    def test_specialist_with_gene_group(self, postgres_session):
        """Test associating specialist with gene group."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"Test Specialist {ts}",
            address=f"Test Address {ts}",
        )
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([specialist, gene_group])
        postgres_session.commit()
        postgres_session.refresh(specialist)
        postgres_session.refresh(gene_group)

        # Create association via junction table
        association = FamHasSpecialist(
            specialist_id=specialist.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()
        postgres_session.refresh(association)

        # Verify the association was created
        assert association.specialist_id == specialist.id
        assert association.gene_group_id == gene_group.id

    def test_query_specialists_by_gene_group(self, postgres_session):
        """Test finding specialists for a gene group."""
        ts = int(time.time() * 1000)
        specialist1 = Specialist(name=f"Specialist 1 {ts}", address=f"Address 1 {ts}")
        specialist2 = Specialist(name=f"Specialist 2 {ts}", address=f"Address 2 {ts}")
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([specialist1, specialist2, gene_group])
        postgres_session.commit()
        postgres_session.refresh(specialist1)
        postgres_session.refresh(specialist2)
        postgres_session.refresh(gene_group)

        # Associate both specialists with the group
        association1 = FamHasSpecialist(
            specialist_id=specialist1.id,
            gene_group_id=gene_group.id,
        )
        association2 = FamHasSpecialist(
            specialist_id=specialist2.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add_all([association1, association2])
        postgres_session.commit()

        # Query specialists for the group using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT specialist.id, specialist.name
                FROM specialist
                JOIN family_has_specialist ON specialist.id = family_has_specialist.specialist_id
                WHERE family_has_specialist.fam_id = :group_id
                ORDER BY specialist.name
            """),
            {"group_id": gene_group.id},
        ).fetchall()

        assert len(result) == 2
        names = {r[1] for r in result}
        assert names == {f"Specialist 1 {ts}", f"Specialist 2 {ts}"}

    def test_query_gene_groups_by_specialist(self, postgres_session):
        """Test finding gene groups for a specialist."""
        ts = int(time.time() * 1000)
        specialist = Specialist(name=f"Query Specialist {ts}", address=f"Test Address {ts}")
        group1 = GeneGroup(name=f"Group 1 {ts}")
        group2 = GeneGroup(name=f"Group 2 {ts}")

        postgres_session.add_all([specialist, group1, group2])
        postgres_session.commit()
        postgres_session.refresh(specialist)
        postgres_session.refresh(group1)
        postgres_session.refresh(group2)

        # Associate specialist with both groups
        association1 = FamHasSpecialist(
            specialist_id=specialist.id,
            gene_group_id=group1.id,
        )
        association2 = FamHasSpecialist(
            specialist_id=specialist.id,
            gene_group_id=group2.id,
        )
        postgres_session.add_all([association1, association2])
        postgres_session.commit()

        # Query groups for the specialist using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT family_new.id, family_new.name
                FROM family_new
                JOIN family_has_specialist ON family_new.id = family_has_specialist.fam_id
                WHERE family_has_specialist.specialist_id = :specialist_id
                ORDER BY family_new.name
            """),
            {"specialist_id": specialist.id},
        ).fetchall()

        assert len(result) == 2
        names = {r[1] for r in result}
        assert names == {f"Group 1 {ts}", f"Group 2 {ts}"}

    def test_remove_specialist_from_gene_group(self, postgres_session):
        """Test removing specialist from gene group."""
        ts = int(time.time() * 1000)
        specialist = Specialist(name=f"Remove Specialist {ts}", address=f"Test Address {ts}")
        gene_group = GeneGroup(name=f"Remove Test Group {ts}")

        postgres_session.add_all([specialist, gene_group])
        postgres_session.commit()
        postgres_session.refresh(specialist)
        postgres_session.refresh(gene_group)

        # Create association
        association = FamHasSpecialist(
            specialist_id=specialist.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        # Verify association exists
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_has_specialist WHERE specialist_id = :sid AND fam_id = :gid"),
            {"sid": specialist.id, "gid": gene_group.id},
        ).scalar()
        assert result == 1

        # Delete association
        postgres_session.delete(association)
        postgres_session.commit()

        # Verify removal
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_has_specialist WHERE specialist_id = :sid AND fam_id = :gid"),
            {"sid": specialist.id, "gid": gene_group.id},
        ).scalar()
        assert result == 0

    def test_manual_delete_associations_when_specialist_deleted(self, postgres_session):
        """Test that associations can be manually deleted along with specialist."""
        ts = int(time.time() * 1000)
        specialist = Specialist(name=f"Manual Delete Specialist {ts}", address=f"Test Address {ts}")
        gene_group = GeneGroup(name=f"Manual Delete Test Group {ts}")

        postgres_session.add_all([specialist, gene_group])
        postgres_session.commit()
        postgres_session.refresh(specialist)
        postgres_session.refresh(gene_group)

        association = FamHasSpecialist(
            specialist_id=specialist.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        # Delete both specialist and association
        postgres_session.delete(association)
        postgres_session.delete(specialist)
        postgres_session.commit()

        # Verify both are deleted
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_has_specialist WHERE specialist_id = :sid"),
            {"sid": specialist.id},
        ).scalar()
        assert result == 0

    def test_manual_delete_associations_when_gene_group_deleted(self, postgres_session):
        """Test that associations can be manually deleted along with gene group."""
        ts = int(time.time() * 1000)
        specialist = Specialist(name=f"Manual Group Delete Specialist {ts}", address=f"Test Address {ts}")
        gene_group = GeneGroup(name=f"Manual Group Delete Test Group {ts}")

        postgres_session.add_all([specialist, gene_group])
        postgres_session.commit()
        postgres_session.refresh(specialist)
        postgres_session.refresh(gene_group)

        association = FamHasSpecialist(
            specialist_id=specialist.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        # Delete both gene_group and association
        postgres_session.delete(association)
        postgres_session.delete(gene_group)
        postgres_session.commit()

        # Verify association is deleted
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_has_specialist WHERE fam_id = :gid"),
            {"gid": gene_group.id},
        ).scalar()
        assert result == 0


@pytest.mark.usefixtures("postgres_session")
class TestSpecialistRepr:
    """Test Specialist __repr__ method."""

    def test_specialist_repr(self, postgres_session):
        """Test Specialist string representation."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"Repr Specialist {ts}",
            address=f"Repr Address {ts}",
        )
        postgres_session.add(specialist)
        postgres_session.commit()

        result = repr(specialist)

        assert "Specialist" in result
        assert f"Repr Specialist {ts}" in result


@pytest.mark.usefixtures("postgres_session")
class TestFamHasSpecialistRepr:
    """Test FamHasSpecialist __repr__ method."""

    def test_family_has_specialist_repr(self, postgres_session):
        """Test FamHasSpecialist string representation."""
        ts = int(time.time() * 1000)
        specialist = Specialist(name=f"Test Specialist {ts}", address=f"Test Address {ts}")
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([specialist, gene_group])
        postgres_session.commit()
        postgres_session.refresh(specialist)
        postgres_session.refresh(gene_group)

        association = FamHasSpecialist(
            specialist_id=specialist.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        result = repr(association)

        assert "FamHasSpecialist" in result
        assert str(specialist.id) in result
        assert str(gene_group.id) in result


@pytest.mark.usefixtures("postgres_session")
class TestSpecialistUrlField:
    """Test Specialist URL field handling."""

    def test_specialist_url_optional(self, postgres_session):
        """Test URL field is optional."""
        ts = int(time.time() * 1000)
        specialist = Specialist(
            name=f"No URL Specialist {ts}",
            address=f"No URL Address {ts}",
        )
        postgres_session.add(specialist)
        postgres_session.commit()

        # Query raw columns - url should be NULL
        result = postgres_session.execute(
            text('SELECT url FROM specialist WHERE id = :id'),
            {"id": specialist.id}
        ).one()

        assert result[0] is None

    def test_specialist_with_various_url_formats(self, postgres_session):
        """Test specialists with various URL formats."""
        ts = int(time.time() * 1000)
        urls = [
            "https://example.com",
            "http://test.org",
            "https://subdomain.domain.com/path",
            "https://example.com:8080/page?query=value",
        ]

        for i, url in enumerate(urls):
            specialist = Specialist(
                name=f"URL Specialist {ts}-{i}",
                address=f"Address {ts}-{i}",
                url=url,
            )
            postgres_session.add(specialist)
        postgres_session.commit()

        # Query and verify URLs are preserved
        stmt = select(Specialist).where(
            Specialist.name.like(f"URL Specialist {ts}-%")
        ).order_by(Specialist.name)
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) == 4
        for i, specialist in enumerate(results):
            assert specialist.url == urls[i]
