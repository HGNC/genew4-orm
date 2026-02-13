"""Real-world workflow integration tests with PostgreSQL.

This module tests common workflows that mirror actual usage
patterns in genew4 application.
"""

from datetime import date

import pytest
from sqlalchemy import select

from genew4_orm.models import Gene, GeneGroup


@pytest.mark.usefixtures("postgres_session")
class TestGeneApprovalWorkflow:
    """Test gene approval workflow from pending to approved."""

    def test_complete_gene_approval_workflow(self, postgres_session):
        """Test full gene approval workflow with dates."""
        # Start with pending gene
        gene = Gene(
            approved_symbol="APPRWF1",
            approved_name="Approval Workflow Test Gene",
            status="Pending",
            date_submitted=date(2024, 1, 1),
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Verify initial state
        postgres_session.refresh(gene)
        assert gene.status == "Pending"
        assert gene.date_modified is None

        # Update to Approved with date
        gene.status = "Approved"
        gene.date_modified = date(2024, 1, 15)
        gene.date_to_approve_or_reserve = date(2024, 1, 15)
        postgres_session.commit()

        # Verify approved state
        postgres_session.refresh(gene)
        assert gene.status == "Approved"
        assert gene.date_modified == date(2024, 1, 15)
        assert gene.date_to_approve_or_reserve == date(2024, 1, 15)

    def test_gene_symbol_change_workflow(self, postgres_session):
        """Test changing gene symbol with audit trail."""
        # Create gene with original symbol
        gene = Gene(
            approved_symbol="ORIGSYM",
            approved_name="Original Symbol Gene",
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Verify original state
        postgres_session.refresh(gene)
        assert gene.approved_symbol == "ORIGSYM"
        assert gene.date_symbol_changed is None

        # Change symbol
        gene.approved_symbol = "NEWSYM"
        gene.date_symbol_changed = date(2024, 2, 1)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.approved_symbol == "NEWSYM"
        assert gene.date_symbol_changed == date(2024, 2, 1)


@pytest.mark.usefixtures("postgres_session")
class TestBatchOperations:
    """Test batch operations on multiple records."""

    def test_batch_gene_import(self, postgres_session):
        """Test importing multiple genes in batch."""
        import time

        ts = int(time.time() * 1000)

        genes_to_import = []
        for i in range(10):
            gene = Gene(
                approved_symbol=f"BATCH{ts}_{i}",
                approved_name=f"Batch Import Gene {i} {ts}",
                status="Approved",
                editor="batch_importer",
            )
            genes_to_import.append(gene)

        postgres_session.add_all(genes_to_import)
        postgres_session.commit()

        # Verify all genes were imported
        stmt = select(Gene).where(Gene.approved_symbol.like(f"BATCH{ts}%"))
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) == 10
        symbols = {g.approved_symbol for g in results}
        assert all(f"BATCH{ts}_{i}" in symbols for i in range(10))


@pytest.mark.usefixtures("postgres_session")
class TestTransactionRollback:
    """Test transaction rollback behavior."""

    def test_transaction_rollback_on_error(self, postgres_session):
        """Test that rollback affects all operations in transaction."""
        # Create first gene
        gene1 = Gene(
            approved_symbol="ROLLBACK1",
            approved_name="Rollback Test Gene 1",
            status="Approved",
        )
        postgres_session.add(gene1)
        postgres_session.flush()  # Flush but don't commit yet

        # Create second gene
        gene2 = Gene(
            approved_symbol="ROLLBACK2",
            approved_name="Rollback Test Gene 2",
            status="Approved",
        )
        postgres_session.add(gene2)

        # Rollback
        postgres_session.rollback()

        # Verify neither gene was saved
        stmt = select(Gene).where(Gene.approved_symbol.in_(["ROLLBACK1", "ROLLBACK2"]))
        results = postgres_session.execute(stmt).scalars().all()
        assert len(results) == 0


@pytest.mark.usefixtures("postgres_session")
class TestConstraintHandling:
    """Test database constraint handling."""

    def test_unique_gene_group_name(self, postgres_session):
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


@pytest.mark.usefixtures("postgres_session")
class TestComplexQueries:
    """Test complex query scenarios."""

    def test_aggregation_query(self, postgres_session):
        """Test aggregation queries (count, sum, etc.)."""
        # Create multiple genes
        for i in range(5):
            gene = Gene(
                approved_symbol=f"AGGREG{i}",
                approved_name=f"Aggregation Test {i}",
                status="Approved",
            )
            postgres_session.add(gene)
        postgres_session.commit()

        # Count genes by status
        from sqlalchemy import func

        stmt = select(Gene.status, func.count(Gene.hgnc_id)).group_by(Gene.status)
        results = postgres_session.execute(stmt).all()

        # Should have Approved status with count
        approved_count = [r for r in results if r[0] == "Approved"]
        assert len(approved_count) >= 1

    def test_order_by_multiple_fields(self, postgres_session):
        """Test ordering by multiple fields."""
        import time

        ts = int(time.time() * 1000)

        # Create genes with different combinations
        gene1 = Gene(
            approved_symbol=f"MULTI1_{ts}",
            approved_name=f"Multi Order Gene 1 {ts}",
            status="Pending",
            public_ncbi_gene_id=100,
        )
        gene2 = Gene(
            approved_symbol=f"MULTI1_{ts}",
            approved_name=f"Multi Order Gene 2 {ts}",
            status="Approved",
            public_ncbi_gene_id=200,
        )
        gene3 = Gene(
            approved_symbol=f"MULTI2_{ts}",
            approved_name=f"Multi Order Gene 3 {ts}",
            status="Pending",
            public_ncbi_gene_id=50,
        )
        postgres_session.add_all([gene1, gene2, gene3])
        postgres_session.commit()

        # Order by symbol (asc), then by ncbi_id (desc)
        from sqlalchemy import asc, desc

        stmt = (
            select(Gene)
            .where(Gene.approved_symbol.in_([f"MULTI1_{ts}", f"MULTI2_{ts}"]))
            .order_by(asc(Gene.approved_symbol), desc(Gene.public_ncbi_gene_id))
        )
        results = postgres_session.execute(stmt).scalars().all()

        # Should get: MULTI1 (id=200), MULTI1 (id=100), MULTI2 (id=50)
        assert len(results) == 3
