"""End-to-end tests for gene lifecycle workflows.

Tests complete gene curation workflow:
- Pending submission
- Approval process
- Symbol modification
- Withdrawal/deletion

Each test verifies entire workflow with audit trail validation.
"""

from datetime import date

import pytest
from sqlalchemy import select

from genew4_orm.enums import GeneStatus
from genew4_orm.models import AuditLog, Gene


@pytest.mark.usefixtures("e2e_session")
class TestGeneLifecycleWorkflow:
    """Test gene lifecycle curation workflow."""

    def test_complete_gene_curation_workflow(self, e2e_session, gene_factory) -> None:
        """Test gene from pending submission through final withdrawal."""
        # Create pending gene (simulating curator submission)
        gene = gene_factory(
            locus_type="gene with protein product",
        )
        e2e_session.add(gene)
        e2e_session.flush()

        # Capture ID for later verification
        gene_id = gene.hgnc_id

        # Verify initial state
        assert gene.status == "Pending"
        assert gene.date_modified is None
        assert gene.date_to_approve_or_reserve is None

        # Approve gene (curator review)
        gene.status = GeneStatus.APPROVED
        gene.date_to_approve_or_reserve = date(2024, 1, 15)
        e2e_session.flush()

        # Modify symbol (nomenclature update)
        gene.approved_symbol = "E2E_GENE1A"
        gene.date_symbol_changed = date(2024, 2, 1)
        e2e_session.flush()

        # Withdraw gene (decommissioning)
        gene.status = "Symbol Withdrawn"
        e2e_session.flush()

        e2e_session.commit()

        # Verify audit trail captured ALL changes
        # Note: CREATE entries have entity_id=0, so we filter by entity_type only
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.entity_type == "Gene",
            )
            .order_by(AuditLog.timestamp)
        )
        all_audit_entries = e2e_session.execute(stmt).scalars().all()

        # Filter to entries related to our gene
        # CREATE entries have entity_id=0, UPDATE entries have the actual gene_id
        audit_entries = []
        create_count = 0
        for entry in all_audit_entries:
            if entry.operation == "CREATE":
                # Check if this CREATE is for our gene by looking at field_changes
                changes = entry.field_changes
                if "approved_symbol" in changes:
                    symbol = changes["approved_symbol"]["new"]
                    if symbol and "E2E_GENE" in str(symbol):
                        create_count += 1
                        audit_entries.append(entry)
            elif entry.entity_id == gene_id:
                audit_entries.append(entry)

        # Should have at least 1 CREATE and 2-3 UPDATEs
        assert len(audit_entries) >= 3, f"Expected at least 3 audit entries, got {len(audit_entries)}"
        assert create_count >= 1, f"Expected at least 1 CREATE entry, got {create_count}"

        operations = [entry.operation for entry in audit_entries]
        assert "CREATE" in operations
        assert "UPDATE" in operations

        # Verify gene still accessible with final status
        retrieved = e2e_session.get(Gene, gene_id)
        assert retrieved.status == "Symbol Withdrawn"
        assert retrieved.approved_symbol == "E2E_GENE1A"
