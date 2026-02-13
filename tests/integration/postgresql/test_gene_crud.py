"""Gene CRUD operations integration tests with PostgreSQL.

This module tests Create, Read, Update, Delete (CRUD) operations for Gene model using actual PostgreSQL genew4 database.
"""

from datetime import date

import pytest
from sqlalchemy import select

from genew4_orm.models import Gene


@pytest.mark.usefixtures("postgres_session")
class TestGeneCRUD:
    """Test Gene CRUD operations with PostgreSQL."""

    def test_create_gene_with_all_fields(self, postgres_session):
        """Test creating gene with all required fields."""
        gene = Gene(
            approved_symbol="TEST1",
            approved_name="Test Gene 1",
            status="Approved",
            locus_type="gene with protein product",
            chromosomal_location="1p36.33",
            public_ncbi_gene_id=12345,
            date_modified=date.today(),
        )
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.hgnc_id is not None
        assert gene.approved_symbol == "TEST1"
        assert gene.approved_name == "Test Gene 1"
        assert gene.status == "Approved"
        assert gene.locus_type == "gene with protein product"

    def test_create_gene_with_minimal_fields(self, postgres_session):
        """Test creating gene with only required fields."""
        gene = Gene(approved_symbol="TEST2", approved_name="Test Gene 2")
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.hgnc_id is not None
        assert gene.approved_symbol == "TEST2"
        assert gene.approved_name == "Test Gene 2"
        # Default values should be applied
        assert gene.locus_type == "undef"
        assert gene.status == "Pending"

    def test_read_gene_by_id(self, postgres_session):
        """Test reading gene by ID."""
        # Create test gene
        gene = Gene(approved_symbol="TEST3", approved_name="Test Gene 3", status="Approved")
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        # Read gene by ID
        retrieved_gene = postgres_session.get(Gene, gene.hgnc_id)
        assert retrieved_gene is not None
        assert retrieved_gene.approved_symbol == "TEST3"
        assert retrieved_gene.approved_name == "Test Gene 3"

    def test_update_gene_fields(self, postgres_session):
        """Test updating gene fields."""
        gene = Gene(approved_symbol="TEST4", approved_name="Test Gene 4", status="Pending")
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        # Update gene
        gene.status = "Approved"
        gene.approved_name = "Updated Test Gene 4"
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.status == "Approved"
        assert gene.approved_name == "Updated Test Gene 4"

    def test_delete_gene(self, postgres_session):
        """Test deleting gene."""
        gene = Gene(approved_symbol="TEST5", approved_name="Test Gene 5")
        postgres_session.add(gene)
        postgres_session.commit()
        gene_hgnc_id = gene.hgnc_id

        # Delete gene
        postgres_session.delete(gene)
        postgres_session.commit()

        # Verify deletion
        deleted_gene = postgres_session.get(Gene, gene_hgnc_id)
        assert deleted_gene is None

    def test_query_genes_by_status(self, postgres_session):
        """Test querying genes by status."""
        # Create test genes with different statuses
        gene1 = Gene(approved_symbol="TEST6A", approved_name="Test Gene 6A", status="Approved")
        gene2 = Gene(approved_symbol="TEST6B", approved_name="Test Gene 6B", status="Pending")
        gene3 = Gene(approved_symbol="TEST6C", approved_name="Test Gene 6C", status="Approved")
        postgres_session.add_all([gene1, gene2, gene3])
        postgres_session.commit()

        # Query approved genes
        stmt = select(Gene).where(Gene.status == "Approved")
        approved_genes = postgres_session.execute(stmt).scalars().all()

        approved_symbols = [g.approved_symbol for g in approved_genes]
        assert "TEST6A" in approved_symbols
        assert "TEST6C" in approved_symbols
        assert "TEST6B" not in approved_symbols

    def test_query_genes_with_wildcard(self, postgres_session):
        """Test querying genes with ILIKE pattern matching."""
        # Use timestamp to ensure unique symbols
        import time

        ts = int(time.time() * 1000)

        # Create test genes with unique symbols to avoid conflicts
        gene1 = Gene(approved_symbol=f"TEST_WILDCARD_A1_{ts}", approved_name=f"Test Wildcard A1 {ts}")
        gene2 = Gene(approved_symbol=f"TEST_WILDCARD_A2_{ts}", approved_name=f"Test Wildcard A2 {ts}")
        gene3 = Gene(approved_symbol=f"TEST_WILDCARD_B1_{ts}", approved_name=f"Test Wildcard B1 {ts}")
        postgres_session.add_all([gene1, gene2, gene3])
        postgres_session.commit()

        # Query with pattern - use pattern that matches TEST_WILDCARD_A1 or A2 followed by timestamp
        stmt = select(Gene).where(Gene.approved_symbol.ilike(f"TEST_WILDCARD_A%_{ts}"))
        result_genes = postgres_session.execute(stmt).scalars().all()

        assert len(result_genes) == 2
        symbols = [g.approved_symbol for g in result_genes]
        assert f"TEST_WILDCARD_A1_{ts}" in symbols
        assert f"TEST_WILDCARD_A2_{ts}" in symbols

    def test_gene_with_date_fields(self, postgres_session):
        """Test gene with date-related fields."""
        test_date = date(2024, 1, 15)
        gene = Gene(
            approved_symbol="TEST7",
            approved_name="Test Gene 7",
            date_submitted=test_date,
            date_modified=test_date,
            date_symbol_changed=test_date,
        )
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.date_submitted == test_date
        assert gene.date_modified == test_date
        assert gene.date_symbol_changed == test_date

    def test_gene_with_external_references(self, postgres_session):
        """Test gene with external database references."""
        gene = Gene(
            approved_symbol="TEST8",
            approved_name="Test Gene 8",
            public_ncbi_gene_id=12345,
            public_ensembl_id="ENSG00000123456",
            public_refseq_ids="NM_001234567",
        )
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.public_ncbi_gene_id == 12345
        assert gene.public_ensembl_id == "ENSG00000123456"
        assert gene.public_refseq_ids == "NM_001234567"

    def test_gene_with_text_fields(self, postgres_session):
        """Test gene with large text fields."""
        long_text = "A" * 1000  # Test large text handling
        gene = Gene(
            approved_symbol="TEST9",
            approved_name="Test Gene 9",
            alias_symbols=long_text,
            previous_names=long_text,
        )
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.alias_symbols == long_text
        assert gene.previous_names == long_text

    def test_gene_with_boolean_fields(self, postgres_session):
        """Test gene with boolean fields."""
        gene = Gene(
            approved_symbol="TEST10",
            approved_name="Test Gene 10",
            ambiguous=True,
            to_review=False,
            tgmi_stable_symbol=True,
        )
        postgres_session.add(gene)
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.ambiguous is True
        assert gene.to_review is False
        assert gene.tgmi_stable_symbol is True

    def test_multiple_genes_create_and_query(self, postgres_session):
        """Test creating multiple genes and querying them."""
        genes = [
            Gene(approved_symbol=f"TEST{i}", approved_name=f"Test Gene {i}", status="Approved") for i in range(11, 16)
        ]
        postgres_session.add_all(genes)
        postgres_session.commit()

        # Query all created genes
        stmt = select(Gene).where(Gene.approved_symbol.like("TEST1%"))
        result_genes = postgres_session.execute(stmt).scalars().all()

        assert len(result_genes) >= 5
        symbols = {g.approved_symbol for g in result_genes}
        for i in range(11, 16):
            assert f"TEST{i}" in symbols

    def test_gene_update_with_multiple_fields(self, postgres_session):
        """Test updating multiple gene fields simultaneously."""
        gene = Gene(
            approved_symbol="TEST17",
            approved_name="Original Name",
            status="Pending",
            locus_type="undef",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Update multiple fields
        gene.approved_name = "Updated Name"
        gene.status = "Approved"
        gene.locus_type = "gene with protein product"
        gene.date_modified = date.today()
        postgres_session.commit()
        postgres_session.refresh(gene)

        assert gene.approved_name == "Updated Name"
        assert gene.status == "Approved"
        assert gene.locus_type == "gene with protein product"
        assert gene.date_modified is not None

    def test_gene_order_by_symbol(self, postgres_session):
        """Test querying genes ordered by symbol."""
        # Use timestamp to ensure unique symbols
        import time

        ts = int(time.time() * 1000)

        # Use unique symbols to avoid conflicts with existing data
        genes = [
            Gene(approved_symbol=f"TEST_ORDER_ZEBRA_{ts}", approved_name=f"Zebra Gene {ts}"),
            Gene(approved_symbol=f"TEST_ORDER_ALPHA_{ts}", approved_name=f"Alpha Gene {ts}"),
            Gene(approved_symbol=f"TEST_ORDER_BETA_{ts}", approved_name=f"Beta Gene {ts}"),
        ]
        postgres_session.add_all(genes)
        postgres_session.commit()

        # Query ordered by symbol
        stmt = (
            select(Gene)
            .where(
                Gene.approved_symbol.in_([f"TEST_ORDER_ZEBRA_{ts}", f"TEST_ORDER_ALPHA_{ts}", f"TEST_ORDER_BETA_{ts}"])
            )
            .order_by(Gene.approved_symbol)
        )
        ordered_genes = postgres_session.execute(stmt).scalars().all()

        assert ordered_genes[0].approved_symbol == f"TEST_ORDER_ALPHA_{ts}"
        assert ordered_genes[1].approved_symbol == f"TEST_ORDER_BETA_{ts}"
        assert ordered_genes[2].approved_symbol == f"TEST_ORDER_ZEBRA_{ts}"
