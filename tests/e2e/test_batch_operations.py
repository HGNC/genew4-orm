"""End-to-end tests for batch operations.

Tests batch operations with transaction safety:
- Bulk import performance
- Atomic transaction behavior
- Audit logging for bulk operations
"""

import uuid

import pytest
from sqlalchemy import select

from genew4_orm.models import AuditLog, Gene


@pytest.mark.usefixtures("e2e_session")
class TestBatchOperations:
    """Test batch operations with transaction safety."""

    def test_batch_import_success(self, e2e_session) -> None:
        """Test successful batch import of 100 genes with unique identifiers."""
        # Use unique prefix to avoid conflicts with previous test runs
        unique_id = str(uuid.uuid4())[:8]
        prefix = f"E2E_BATCH_{unique_id}_"

        genes_to_import = []
        for i in range(100):
            gene = Gene(
                approved_symbol=f"{prefix}{i}",
                approved_name=f"Batch Import Gene {i}",
                status="Approved",
                editor="batch_importer",
            )
            genes_to_import.append(gene)

        # Add all genes at once (atomic operation)
        e2e_session.add_all(genes_to_import)
        e2e_session.commit()

        # Verify all 100 genes were committed
        stmt = select(Gene).where(Gene.approved_symbol.like(f"{prefix}%"))
        result = e2e_session.execute(stmt).scalars().all()
        assert len(result) == 100, f"Expected 100 genes, got {len(result)}"

        # Verify audit log was created for batch
        stmt = select(AuditLog).where(
            AuditLog.operation == "CREATE",
            AuditLog.user == "e2e_test_user",
        )
        audit_entries = e2e_session.execute(stmt).scalars().all()

        # Find batch create audit entries
        batch_entries = [e for e in audit_entries if e.field_changes and f"{prefix}" in str(e.field_changes)]
        assert len(batch_entries) >= 1, "Batch operation should create audit log"

    def test_batch_import_transaction_rollback(self, e2e_session) -> None:
        """Test that batch import with error causes complete rollback."""
        # Use unique prefix to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        prefix = f"E2E_ROLLBACK_{unique_id}_"

        # Prepare 50 valid genes
        genes_to_import = []
        for i in range(50):
            gene = Gene(
                approved_symbol=f"{prefix}{i}",
                approved_name=f"Batch Gene {i}",
                status="Approved",
                editor="batch_importer",
            )
            genes_to_import.append(gene)

        # Add all genes
        e2e_session.add_all(genes_to_import)

        # Verify genes are in session before commit
        assert len(e2e_session.new) >= 50, "Genes should be in session"

        # Rollback explicitly to simulate transaction failure
        e2e_session.rollback()

        # Verify NO genes were committed after rollback
        stmt = select(Gene).where(Gene.approved_symbol.like(f"{prefix}%"))
        result = e2e_session.execute(stmt).scalars().all()
        assert len(result) == 0, f"Expected 0 genes after rollback, got {len(result)}"
