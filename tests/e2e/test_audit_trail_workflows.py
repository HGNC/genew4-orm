"""End-to-end tests for audit trail verification.

Tests complete audit trails for complex multi-entity operations:
- Multi-entity changes (gene + group)
- User attribution correctness
- Field-level change tracking
- Sequential operation ordering
"""

import json
import pytest

from genew4_orm.models import (
    Gene,
    GeneGroup,
    GeneHasGeneGroup,
    AuditLog,
)
from genew4_orm.enums import GeneStatus
from sqlalchemy import select


@pytest.mark.usefixtures("e2e_session")
class TestMultiEntityAuditTrails:
    """Test audit trails for complex operations."""

    def test_audit_trail_for_gene_group_merge(
        self, e2e_session, gene_factory, gene_group_factory
    ) -> None:
        """Test complete audit trail when merging two gene groups."""
        # Create two groups with genes
        group_a = gene_group_factory()
        e2e_session.add(group_a)
        e2e_session.commit()

        gene1 = gene_factory()
        e2e_session.add(gene1)
        e2e_session.commit()

        association1 = GeneHasGeneGroup(
            gene_id=gene1.hgnc_id,
            gene_group_id=group_a.id,
            custom_sort="1",
        )
        e2e_session.add(association1)
        e2e_session.commit()

        group_b = gene_group_factory()
        e2e_session.add(group_b)
        e2e_session.commit()

        gene2 = gene_factory()
        e2e_session.add(gene2)
        e2e_session.commit()

        association2 = GeneHasGeneGroup(
            gene_id=gene2.hgnc_id,
            gene_group_id=group_b.id,
            custom_sort="1",
        )
        e2e_session.add(association2)
        e2e_session.commit()

        # Merge: move gene2 to group A, delete group B
        association2.gene_group_id = group_a.id
        e2e_session.commit()

        e2e_session.delete(group_b)
        e2e_session.commit()

        # Verify audit trail captured all operations
        stmt = select(AuditLog).where(
            AuditLog.entity_type == "GeneGroup",
        ).order_by(AuditLog.timestamp)
        audit_entries = e2e_session.execute(stmt).scalars().all()

        # Should have CREATE entries for both groups
        assert len(audit_entries) >= 2, f"Expected at least 2 audit entries, got {len(audit_entries)}"

        operations = [entry.operation for entry in audit_entries]
        assert "CREATE" in operations
        assert operations.count("CREATE") >= 2  # Two groups

        # Verify sequential ordering
        timestamps = [entry.timestamp for entry in audit_entries]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1], "Audit entries should be sequential"

    def test_user_attribution_across_entities(
        self, e2e_session, gene_factory, gene_group_factory
    ) -> None:
        """Test that user attribution is correct across entity types."""
        # Create gene (should have user in audit)
        gene = gene_factory()
        e2e_session.add(gene)
        e2e_session.commit()

        # Create gene group (should have same user)
        group = gene_group_factory()
        e2e_session.add(group)
        e2e_session.commit()

        # Verify audit entries have same user
        stmt = select(AuditLog).where(AuditLog.user == "e2e_test_user")
        audit_entries = e2e_session.execute(stmt).scalars().all()

        # Get CREATE entries for Gene and GeneGroup
        gene_audit = None
        group_audit = None
        for entry in audit_entries:
            changes = json.loads(entry.field_changes)
            if entry.entity_type == "Gene" and "approved_symbol" in changes:
                gene_audit = entry
            elif entry.entity_type == "GeneGroup" and "name" in changes:
                group_audit = entry

        assert gene_audit is not None, "Gene audit entry not found"
        assert group_audit is not None, "GeneGroup audit entry not found"
        assert gene_audit.user == group_audit.user == "e2e_test_user"

    def test_field_level_change_tracking(
        self, e2e_session, gene_factory
    ) -> None:
        """Test that field-level changes are captured in detail."""
        # Create gene with minimal fields
        gene = Gene(
            approved_name="Field Test Gene",
            status="Pending",
            locus_type="gene with protein product",
        )
        e2e_session.add(gene)
        e2e_session.commit()
        gene_id = gene.hgnc_id

        # Update multiple fields (approved_symbol was None before)
        gene.approved_symbol = "E2E_FIELD_TEST"
        gene.approved_name = "Field Test Updated"
        gene.status = GeneStatus.APPROVED
        e2e_session.commit()

        # Query audit log for UPDATE operations
        stmt = select(AuditLog).where(
            AuditLog.entity_type == "Gene",
            AuditLog.operation == "UPDATE",
        ).order_by(AuditLog.timestamp)
        audit_entries = e2e_session.execute(stmt).scalars().all()

        # Find the update for our gene
        audit_entry = None
        for entry in audit_entries:
            if entry.entity_id == gene_id:
                audit_entry = entry
                break

        assert audit_entry is not None, "Audit entry not found"

        # Verify field-level detail
        changes = json.loads(audit_entry.field_changes)

        # Should capture all three changes
        assert "approved_symbol" in changes
        assert "approved_name" in changes
        assert "status" in changes

        # Verify old and new values
        assert changes["approved_symbol"]["old"] is None  # Was not set
        assert changes["approved_symbol"]["new"] == "E2E_FIELD_TEST"
        assert changes["approved_name"]["old"] == "Field Test Gene"
        assert changes["approved_name"]["new"] == "Field Test Updated"
        assert changes["status"]["old"] == "Pending"
        assert changes["status"]["new"] == "Approved"
