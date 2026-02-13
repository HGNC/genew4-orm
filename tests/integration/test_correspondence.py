"""Integration tests for Correspondence model with PostgreSQL.

This module tests Correspondence CRUD operations with real database connections,
including testing relationships with GeneGroup.
"""

import time

import pytest
from sqlalchemy import select, text

from genew4_orm.models.correspondence import Correspondence
from genew4_orm.models.gene_group import GeneGroup
from genew4_orm.models.fam_has_corr import FamHasCorr


@pytest.mark.usefixtures("postgres_session")
class TestCorrespondenceCRUD:
    """Test Correspondence CRUD operations with PostgreSQL."""

    def test_create_correspondence_minimal(self, postgres_session):
        """Test creating correspondence with minimal required fields."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Test First {ts}",
            email=f"test{ts}@example.com",
        )
        postgres_session.add(corr)
        postgres_session.commit()
        postgres_session.refresh(corr)

        assert corr.id is not None
        assert corr.first_name == f"Test First {ts}"
        assert corr.email == f"test{ts}@example.com"

    def test_create_correspondence_with_all_fields(self, postgres_session):
        """Test creating correspondence with all fields."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Complete First {ts}",
            last_name=f"Complete Last {ts}",
            email=f"complete{ts}@example.com",
            address=f"123 Test St, Test City {ts}",
            date_received=f"2024-01-15",
            date_sent=f"2024-01-16",
        )
        postgres_session.add(corr)
        postgres_session.commit()
        postgres_session.refresh(corr)

        assert corr.first_name == f"Complete First {ts}"
        assert corr.last_name == f"Complete Last {ts}"
        assert corr.email == f"complete{ts}@example.com"
        assert corr.address == f"123 Test St, Test City {ts}"
        assert corr.date_received == "2024-01-15"
        assert corr.date_sent == "2024-01-16"

    def test_read_correspondence_by_id(self, postgres_session):
        """Test reading correspondence by ID."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Read Test First {ts}",
            email=f"read{ts}@example.com",
        )
        postgres_session.add(corr)
        postgres_session.commit()
        corr_id = corr.id

        # Read by ID
        retrieved_corr = postgres_session.get(Correspondence, corr_id)

        assert retrieved_corr is not None
        assert retrieved_corr.first_name == f"Read Test First {ts}"
        assert retrieved_corr.email == f"read{ts}@example.com"

    def test_update_correspondence_fields(self, postgres_session):
        """Test updating correspondence fields."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Original First {ts}",
            email=f"original{ts}@example.com",
        )
        postgres_session.add(corr)
        postgres_session.commit()

        # Update fields
        corr.first_name = f"Updated First {ts}"
        corr.last_name = f"Updated Last {ts}"
        corr.email = f"updated{ts}@example.com"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(corr)
        assert corr.first_name == f"Updated First {ts}"
        assert corr.last_name == f"Updated Last {ts}"
        assert corr.email == f"updated{ts}@example.com"

    def test_delete_correspondence(self, postgres_session):
        """Test deleting correspondence."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Delete Test First {ts}",
            email=f"delete{ts}@example.com",
        )
        postgres_session.add(corr)
        postgres_session.commit()
        corr_id = corr.id

        # Delete correspondence
        postgres_session.delete(corr)
        postgres_session.commit()

        # Verify deletion
        deleted_corr = postgres_session.get(Correspondence, corr_id)
        assert deleted_corr is None

    def test_query_correspondence_by_email(self, postgres_session):
        """Test querying correspondence by email pattern."""
        ts = int(time.time() * 1000)
        # Create multiple correspondence records
        for i in range(3):
            corr = Correspondence(
                first_name=f"Query First {i}",
                email=f"query{i}_{ts}@example.com",
            )
            postgres_session.add(corr)
        postgres_session.commit()

        # Query with wildcard
        stmt = select(Correspondence).where(
            Correspondence.email.like(f"%_{ts}@example.com")
        ).order_by(Correspondence.email)
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) == 3


@pytest.mark.usefixtures("postgres_session")
class TestCorrespondenceGeneGroupRelationship:
    """Test Correspondence relationship with GeneGroup via FamHasCorr."""

    def test_correspondence_with_gene_group(self, postgres_session):
        """Test associating correspondence with a gene group."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Test First {ts}",
            email=f"group{ts}@example.com",
        )
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([corr, gene_group])
        postgres_session.commit()
        postgres_session.refresh(corr)
        postgres_session.refresh(gene_group)

        # Create association via junction table
        association = FamHasCorr(
            correspondence_id=corr.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        # Verify the association was created
        assert association.correspondence_id == corr.id
        assert association.gene_group_id == gene_group.id

    def test_query_correspondence_by_gene_group(self, postgres_session):
        """Test finding correspondence for a gene group."""
        ts = int(time.time() * 1000)
        corr1 = Correspondence(first_name=f"Query Corr 1 {ts}", email=f"corr1{ts}@example.com")
        corr2 = Correspondence(first_name=f"Query Corr 2 {ts}", email=f"corr2{ts}@example.com")
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([corr1, corr2, gene_group])
        postgres_session.commit()
        postgres_session.refresh(corr1)
        postgres_session.refresh(corr2)
        postgres_session.refresh(gene_group)

        # Associate both correspondence with the group
        association1 = FamHasCorr(
            correspondence_id=corr1.id,
            gene_group_id=gene_group.id,
        )
        association2 = FamHasCorr(
            correspondence_id=corr2.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add_all([association1, association2])
        postgres_session.commit()

        # Query correspondence for the group using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT corr.corr_id, corr.corr_first_name, corr.corr_email
                FROM corr
                JOIN family_has_correspondence ON corr.corr_id = family_has_correspondence.corr_id
                WHERE family_has_correspondence.fam_id = :group_id
                ORDER BY corr.corr_first_name
            """),
            {"group_id": gene_group.id},
        ).fetchall()

        assert len(result) == 2
        names = {r[1] for r in result}
        assert names == {f"Query Corr 1 {ts}", f"Query Corr 2 {ts}"}

    def test_remove_correspondence_from_gene_group(self, postgres_session):
        """Test removing correspondence from gene group."""
        ts = int(time.time() * 1000)
        corr = Correspondence(first_name=f"Remove Corr {ts}", email=f"remove{ts}@example.com")
        gene_group = GeneGroup(name=f"Remove Test Group {ts}")

        postgres_session.add_all([corr, gene_group])
        postgres_session.commit()
        postgres_session.refresh(corr)
        postgres_session.refresh(gene_group)

        # Create association
        association = FamHasCorr(
            correspondence_id=corr.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        # Verify association exists
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_has_correspondence WHERE corr_id = :cid AND fam_id = :gid"),
            {"cid": corr.id, "gid": gene_group.id},
        ).scalar()
        assert result == 1

        # Delete association
        postgres_session.delete(association)
        postgres_session.commit()

        # Verify removal
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM family_has_correspondence WHERE corr_id = :cid AND fam_id = :gid"),
            {"cid": corr.id, "gid": gene_group.id},
        ).scalar()
        assert result == 0


@pytest.mark.usefixtures("postgres_session")
class TestCorrespondenceRepr:
    """Test Correspondence __repr__ method."""

    def test_correspondence_repr(self, postgres_session):
        """Test Correspondence string representation."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Repr First {ts}",
            email=f"repr{ts}@example.com",
        )
        postgres_session.add(corr)
        postgres_session.commit()

        result = repr(corr)

        assert "Correspondence" in result
        assert f"repr{ts}@example.com" in result


@pytest.mark.usefixtures("postgres_session")
class TestFamHasCorrRepr:
    """Test FamHasCorr __repr__ method."""

    def test_fam_has_corr_repr(self, postgres_session):
        """Test FamHasCorr string representation."""
        ts = int(time.time() * 1000)
        corr = Correspondence(first_name=f"Test Corr {ts}", email=f"testcorr{ts}@example.com")
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([corr, gene_group])
        postgres_session.commit()
        postgres_session.refresh(corr)
        postgres_session.refresh(gene_group)

        association = FamHasCorr(
            correspondence_id=corr.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        result = repr(association)

        assert "FamHasCorr" in result
        assert str(corr.id) in result
        assert str(gene_group.id) in result


@pytest.mark.usefixtures("postgres_session")
class TestCorrespondenceNotes:
    """Test Correspondence notes field."""

    def test_correspondence_with_notes(self, postgres_session):
        """Test creating correspondence with notes."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Notes Test {ts}",
            email=f"notes{ts}@example.com",
            notes="These are important notes about the correspondence.",
        )
        postgres_session.add(corr)
        postgres_session.commit()
        postgres_session.refresh(corr)

        assert corr.notes == "These are important notes about the correspondence."

    def test_update_correspondence_notes(self, postgres_session):
        """Test updating correspondence notes."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Update Notes Test {ts}",
            email=f"updatenotes{ts}@example.com",
            notes="Original notes",
        )
        postgres_session.add(corr)
        postgres_session.commit()

        # Update notes
        corr.notes = "Updated notes"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(corr)
        assert corr.notes == "Updated notes"


@pytest.mark.usefixtures("postgres_session")
class TestCorrespondenceEmailFields:
    """Test Correspondence email fields."""

    def test_correspondence_with_all_email_fields(self, postgres_session):
        """Test correspondence with all email-related fields."""
        ts = int(time.time() * 1000)
        corr = Correspondence(
            first_name=f"Email Test {ts}",
            email=f"email{ts}@example.com",
            email_received="Incoming message content",
            email_sent="Outgoing response content",
        )
        postgres_session.add(corr)
        postgres_session.commit()
        postgres_session.refresh(corr)

        assert corr.email_received == "Incoming message content"
        assert corr.email_sent == "Outgoing response content"

    def test_query_correspondence_with_email_received(self, postgres_session):
        """Test querying correspondence that has received email."""
        ts = int(time.time() * 1000)
        corr1 = Correspondence(
            first_name=f"Received Test {ts}",
            email=f"received{ts}@example.com",
            email_received="Has received email",
        )
        corr2 = Correspondence(
            first_name=f"No Received Test {ts}",
            email=f"noreceived{ts}@example.com",
        )
        postgres_session.add_all([corr1, corr2])
        postgres_session.commit()

        # Query correspondence with email_received
        stmt = select(Correspondence).where(
            Correspondence.email_received.isnot(None)
        )
        results = postgres_session.execute(stmt).scalars().all()

        # Should include only the first
        assert len(results) >= 1
        assert any(r.email == f"received{ts}@example.com" for r in results)


@pytest.mark.usefixtures("postgres_session")
class TestCorrespondenceOptionalFields:
    """Test Correspondence optional fields."""


    def test_correspondence_address_field(self, postgres_session):
        """Test correspondence address field."""
        ts = int(time.time() * 1000)
        address = f"456 Address Ave, Suite 100, City {ts}, TC 12345"
        corr = Correspondence(
            first_name=f"Address Test {ts}",
            email=f"address{ts}@example.com",
            address=address,
        )
        postgres_session.add(corr)
        postgres_session.commit()
        postgres_session.refresh(corr)

        assert corr.address == address
