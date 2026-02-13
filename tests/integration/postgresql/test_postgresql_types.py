"""PostgreSQL-specific data types integration tests.

This module tests PostgreSQL-specific data types including:
- TEXT type (unlimited length text fields)
- Boolean fields
- Date fields
- String fields with various lengths
- Integer fields
- Raw SQL queries
"""

from datetime import date

import pytest
from sqlalchemy import text

from genew4_orm.models import Gene, GeneGroup


@pytest.mark.usefixtures("postgres_session")
class TestTextFields:
    """Test PostgreSQL TEXT type handling."""

    def test_long_text_field_storage(self, postgres_session):
        """Test storing very long text in TEXT fields."""
        long_text = "A" * 10000  # 10,000 characters

        gene = Gene(
            approved_symbol="LONGTEXT",
            approved_name=long_text,
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert len(gene.approved_name) == 10000
        assert gene.approved_name == long_text

    def test_text_field_with_newlines(self, postgres_session):
        """Test that newlines are preserved in TEXT fields."""
        multi_line_text = """Line 1
Line 2
Line 3
  Indented Line 4
Line 5"""

        gene = Gene(
            approved_symbol="NEWLINE",
            approved_name=multi_line_text,
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert "\n" in gene.approved_name
        assert gene.approved_name == multi_line_text

    def test_text_field_with_special_chars(self, postgres_session):
        """Test TEXT fields with special characters."""
        special_text = "Test with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?~`"

        gene = Gene(
            approved_symbol="SPECIAL",
            approved_name=special_text,
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.approved_name == special_text

    def test_text_field_unicode(self, postgres_session):
        """Test TEXT fields with Unicode characters."""
        unicode_text = "测试基因 - Chinese characters, and emoji: 🧬🧪🔬"

        gene = Gene(
            approved_symbol="UNICODE",
            approved_name=unicode_text,
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert "测试基因" in gene.approved_name
        assert "🧬" in gene.approved_name
        assert gene.approved_name == unicode_text

    def test_text_field_null_to_value(self, postgres_session):
        """Test updating TEXT field from NULL to value."""
        gene = Gene(
            approved_symbol="NULLTEST",
            approved_name="Initial value",
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Set to NULL
        postgres_session.refresh(gene)
        gene.approved_name = None
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.approved_name is None

        # Set back to value
        gene.approved_name = "New value after NULL"
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.approved_name == "New value after NULL"


@pytest.mark.usefixtures("postgres_session")
class TestBooleanFields:
    """Test PostgreSQL Boolean type handling."""

    def test_boolean_true_values(self, postgres_session):
        """Test setting Boolean fields to True."""
        gene = Gene(
            approved_symbol="BOOLTRUE",
            approved_name="Boolean True Test",
            status="Approved",
            ambiguous=True,
            to_review=True,
            tgmi_stable_symbol=True,
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.ambiguous is True
        assert gene.to_review is True
        assert gene.tgmi_stable_symbol is True

    def test_boolean_false_values(self, postgres_session):
        """Test setting Boolean fields to False."""
        gene = Gene(
            approved_symbol="BOOLFALSE",
            approved_name="Boolean False Test",
            status="Approved",
            ambiguous=False,
            to_review=False,
            tgmi_stable_symbol=False,
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.ambiguous is False
        assert gene.to_review is False
        assert gene.tgmi_stable_symbol is False

    def test_boolean_null_values(self, postgres_session):
        """Test Boolean fields with NULL values."""
        gene = Gene(
            approved_symbol="BOOLNULL",
            approved_name="Boolean NULL Test",
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.ambiguous is None
        assert gene.to_review is None
        assert gene.tgmi_stable_symbol is None

    def test_boolean_update(self, postgres_session):
        """Test updating Boolean fields."""
        gene = Gene(
            approved_symbol="BOOLUPD",
            approved_name="Boolean Update Test",
            status="Approved",
            ambiguous=False,
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Update to True
        postgres_session.refresh(gene)
        gene.ambiguous = True
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.ambiguous is True

        # Update back to False
        gene.ambiguous = False
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.ambiguous is False


@pytest.mark.usefixtures("postgres_session")
class TestDateFields:
    """Test PostgreSQL Date type handling."""

    def test_date_field_storage(self, postgres_session):
        """Test storing date values."""
        gene = Gene(
            approved_symbol="DATESTORE",
            approved_name="Date Storage Test",
            status="Approved",
            date_modified=date(2024, 1, 15),
            date_to_approve_or_reserve=date(2024, 2, 1),
            date_symbol_changed=date(2024, 1, 10),
            date_name_changed=date(2024, 1, 5),
            date_stable_symbol_changed=date(2024, 1, 20),
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.date_modified == date(2024, 1, 15)
        assert gene.date_to_approve_or_reserve == date(2024, 2, 1)
        assert gene.date_symbol_changed == date(2024, 1, 10)
        assert gene.date_name_changed == date(2024, 1, 5)
        assert gene.date_stable_symbol_changed == date(2024, 1, 20)

    def test_date_field_null_values(self, postgres_session):
        """Test date fields with NULL values."""
        gene = Gene(
            approved_symbol="DATENULL",
            approved_name="Date NULL Test",
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.date_modified is None
        assert gene.date_to_approve_or_reserve is None
        assert gene.date_symbol_changed is None

    def test_date_field_update(self, postgres_session):
        """Test updating date fields."""
        gene = Gene(
            approved_symbol="DATEUPD",
            approved_name="Date Update Test",
            status="Approved",
            date_modified=date(2024, 1, 1),
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Update date
        postgres_session.refresh(gene)
        gene.date_modified = date(2024, 6, 15)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.date_modified == date(2024, 6, 15)


@pytest.mark.usefixtures("postgres_session")
class TestStringFields:
    """Test PostgreSQL VARCHAR type handling."""

    def test_varchar_max_length(self, postgres_session):
        """Test VARCHAR fields at max length."""
        # GeneGroup.abbreviation has max_length=50
        long_abbreviation = "A" * 50

        gene_group = GeneGroup(name="Max Length Test", abbreviation=long_abbreviation)
        postgres_session.add(gene_group)
        postgres_session.commit()

        postgres_session.refresh(gene_group)
        assert len(gene_group.abbreviation) == 50
        assert gene_group.abbreviation == long_abbreviation

    def test_varchar_unicode(self, postgres_session):
        """Test VARCHAR fields with Unicode."""
        gene_group = GeneGroup(
            name="Unicode 测试组",
            abbreviation="UNI代码",
        )
        postgres_session.add(gene_group)
        postgres_session.commit()

        postgres_session.refresh(gene_group)
        assert "测试组" in gene_group.name
        assert gene_group.abbreviation == "UNI代码"

    def test_varchar_empty_string(self, postgres_session):
        """Test VARCHAR fields with empty string."""
        gene = Gene(
            approved_symbol="EMPTYVAR",
            approved_name="Empty Varchar Test",
            status="Approved",
            chromosomal_location="",  # Empty string
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.chromosomal_location == ""

    def test_varchar_update(self, postgres_session):
        """Test updating VARCHAR fields."""
        gene_group = GeneGroup(name="Update Test", abbreviation="OLD")
        postgres_session.add(gene_group)
        postgres_session.commit()

        # Update varchar field
        postgres_session.refresh(gene_group)
        gene_group.abbreviation = "NEW"
        postgres_session.commit()

        postgres_session.refresh(gene_group)
        assert gene_group.abbreviation == "NEW"


@pytest.mark.usefixtures("postgres_session")
class TestIntegerFields:
    """Test PostgreSQL Integer type handling."""

    def test_integer_field_positive(self, postgres_session):
        """Test positive integer values."""
        gene = Gene(
            approved_symbol="INTPOS",
            approved_name="Integer Positive Test",
            status="Approved",
            public_ncbi_gene_id=123456789,
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.public_ncbi_gene_id == 123456789

    def test_integer_field_zero(self, postgres_session):
        """Test integer field with zero."""
        gene = Gene(
            approved_symbol="INTZERO",
            approved_name="Integer Zero Test",
            status="Approved",
            public_ncbi_gene_id=0,
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.public_ncbi_gene_id == 0

    def test_integer_field_null(self, postgres_session):
        """Test integer field with NULL."""
        gene = Gene(
            approved_symbol="INTNULL",
            approved_name="Integer NULL Test",
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        postgres_session.refresh(gene)
        assert gene.public_ncbi_gene_id is None


@pytest.mark.usefixtures("postgres_session")
class TestRawSqlQueries:
    """Test raw SQL queries with PostgreSQL-specific features."""

    def test_raw_text_query(self, postgres_session):
        """Test raw SQL query with TEXT field."""
        # Create test gene
        gene = Gene(
            approved_symbol="RAWSQL1",
            approved_name="Raw SQL Test",
            status="Approved",
        )
        postgres_session.add(gene)
        postgres_session.commit()

        # Query using raw SQL
        result = postgres_session.execute(
            text("SELECT hgnc_app_name FROM hgnc WHERE hgnc_app_sym = :symbol"),
            {"symbol": "RAWSQL1"},
        ).fetchone()

        assert result is not None
        assert result[0] == "Raw SQL Test"

    def test_raw_ilike_query(self, postgres_session):
        """Test raw SQL with ILIKE (case-insensitive)."""
        import time

        ts = int(time.time() * 1000)

        gene1 = Gene(approved_symbol=f"ILIKE1_{ts}", approved_name=f"Test Gene 1 {ts}", status="Approved")
        gene2 = Gene(approved_symbol=f"ILIKE2_{ts}", approved_name=f"Test Gene 2 {ts}", status="Approved")
        postgres_session.add_all([gene1, gene2])
        postgres_session.commit()

        # Query with ILIKE - use pattern that matches our unique symbols
        result = postgres_session.execute(
            text("SELECT hgnc_id FROM hgnc WHERE hgnc_app_sym ILIKE :pattern"),
            {"pattern": f"ilike%_{ts}"},
        ).fetchall()

        assert len(result) == 2
