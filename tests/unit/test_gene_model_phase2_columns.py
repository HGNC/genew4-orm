"""Unit tests for Gene model Phase 2 columns.

Validate that the 5 new columns required by Phase 2 services
(ccds_ids, hseq_ids, public_hseq_id, pseudogene_id, vega_ids)
exist on the Gene model with correct DB column name mappings and types.
"""

import pytest
from sqlalchemy import Column, Integer, Text, inspect

from genew4_orm.models.gene import Gene


class TestGenePhase2Columns:
    """Test cases for Gene model Phase 2 columns."""

    @pytest.fixture()
    def gene_columns(self) -> dict[str, Column]:
        """Return a dict of column name -> Column for the Gene model."""
        return {c.name: c for c in inspect(Gene).columns}

    def test_gene_has_ccds_ids_column(self, gene_columns: dict[str, Column]) -> None:
        """Assert Gene has hgnc_ccds_ids column mapped to ccds_ids attribute."""
        assert "hgnc_ccds_ids" in gene_columns

    def test_gene_has_hseq_ids_column(self, gene_columns: dict[str, Column]) -> None:
        """Assert Gene has hgnc_hseq_ids column mapped to hseq_ids attribute."""
        assert "hgnc_hseq_ids" in gene_columns

    def test_gene_has_public_hseq_id_column(self, gene_columns: dict[str, Column]) -> None:
        """Assert Gene has hgnc_pub_hseq_id column mapped to public_hseq_id attribute."""
        assert "hgnc_pub_hseq_id" in gene_columns

    def test_gene_has_pseudogene_id_column(self, gene_columns: dict[str, Column]) -> None:
        """Assert Gene has hgnc_pseudogene_id column mapped to pseudogene_id attribute."""
        assert "hgnc_pseudogene_id" in gene_columns

    def test_gene_has_vega_ids_column(self, gene_columns: dict[str, Column]) -> None:
        """Assert Gene has hgnc_vega_ids column mapped to vega_ids attribute."""
        assert "hgnc_vega_ids" in gene_columns

    def test_ccds_ids_is_text_nullable(self, gene_columns: dict[str, Column]) -> None:
        """Assert hgnc_ccds_ids is Text type and nullable."""
        col = gene_columns["hgnc_ccds_ids"]
        assert isinstance(col.type, Text)
        assert col.nullable is True

    def test_hseq_ids_is_text_nullable(self, gene_columns: dict[str, Column]) -> None:
        """Assert hgnc_hseq_ids is Text type and nullable."""
        col = gene_columns["hgnc_hseq_ids"]
        assert isinstance(col.type, Text)
        assert col.nullable is True

    def test_public_hseq_id_is_text_nullable(self, gene_columns: dict[str, Column]) -> None:
        """Assert hgnc_pub_hseq_id is Text type and nullable."""
        col = gene_columns["hgnc_pub_hseq_id"]
        assert isinstance(col.type, Text)
        assert col.nullable is True

    def test_pseudogene_id_is_integer_nullable(self, gene_columns: dict[str, Column]) -> None:
        """Assert hgnc_pseudogene_id is Integer type and nullable."""
        col = gene_columns["hgnc_pseudogene_id"]
        assert isinstance(col.type, Integer)
        assert col.nullable is True

    def test_vega_ids_is_text_nullable(self, gene_columns: dict[str, Column]) -> None:
        """Assert hgnc_vega_ids is Text type and nullable."""
        col = gene_columns["hgnc_vega_ids"]
        assert isinstance(col.type, Text)
        assert col.nullable is True

    def test_gene_ccds_ids_attribute_default_none(self) -> None:
        """Assert ccds_ids attribute defaults to None."""
        gene = Gene()
        assert gene.ccds_ids is None

    def test_gene_hseq_ids_attribute_default_none(self) -> None:
        """Assert hseq_ids attribute defaults to None."""
        gene = Gene()
        assert gene.hseq_ids is None

    def test_gene_public_hseq_id_attribute_default_none(self) -> None:
        """Assert public_hseq_id attribute defaults to None."""
        gene = Gene()
        assert gene.public_hseq_id is None

    def test_gene_pseudogene_id_attribute_default_none(self) -> None:
        """Assert pseudogene_id attribute defaults to None."""
        gene = Gene()
        assert gene.pseudogene_id is None

    def test_gene_vega_ids_attribute_default_none(self) -> None:
        """Assert vega_ids attribute defaults to None."""
        gene = Gene()
        assert gene.vega_ids is None

    def test_gene_ccds_ids_attribute_settable(self) -> None:
        """Assert ccds_ids can be set and retrieved."""
        gene = Gene(ccds_ids="CCDS1,CCDS2")
        assert gene.ccds_ids == "CCDS1,CCDS2"

    def test_gene_hseq_ids_attribute_settable(self) -> None:
        """Assert hseq_ids can be set and retrieved."""
        gene = Gene(hseq_ids="HSEQ1,HSEQ2")
        assert gene.hseq_ids == "HSEQ1,HSEQ2"

    def test_gene_public_hseq_id_attribute_settable(self) -> None:
        """Assert public_hseq_id can be set and retrieved."""
        gene = Gene(public_hseq_id="HSEQ123")
        assert gene.public_hseq_id == "HSEQ123"

    def test_gene_pseudogene_id_attribute_settable(self) -> None:
        """Assert pseudogene_id can be set and retrieved."""
        gene = Gene(pseudogene_id=42)
        assert gene.pseudogene_id == 42

    def test_gene_vega_ids_attribute_settable(self) -> None:
        """Assert vega_ids can be set and retrieved."""
        gene = Gene(vega_ids="OTTHUMG000001234")
        assert gene.vega_ids == "OTTHUMG000001234"
