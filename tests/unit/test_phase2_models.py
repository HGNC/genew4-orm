"""Unit tests for Phase 2 ORM models.

Validate that all 10 new SQLModel classes exist with correct
__tablename__, column names, column types, primary keys, and nullability.
"""

import pytest
from db_common import DeclarativeBase
from sqlalchemy import Column, DateTime, Integer, String, Text, inspect


class TestTableModDate:
    """Test cases for TableModDate model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.table_mod_date import TableModDate

        return {c.name: c for c in inspect(TableModDate).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.table_mod_date import TableModDate

        assert TableModDate.__tablename__ == "table_mod_dates"

    def test_is_declarative_base_subclass(self) -> None:
        from genew4_orm.models.table_mod_date import TableModDate

        assert issubclass(TableModDate, DeclarativeBase)

    def test_table_name_column(self, columns: dict[str, Column]) -> None:
        col = columns["table_name"]
        assert col.primary_key is True
        assert hasattr(col.type, "length")

    def test_version_column(self, columns: dict[str, Column]) -> None:
        col = columns["version"]
        assert isinstance(col.type, String)
        assert col.nullable is True

    def test_version_type_column(self, columns: dict[str, Column]) -> None:
        col = columns["version_type"]
        assert isinstance(col.type, String)
        assert col.nullable is True

    def test_mod_date_column(self, columns: dict[str, Column]) -> None:
        col = columns["mod_date"]
        assert isinstance(col.type, DateTime)
        assert col.nullable is True


class TestCcds:
    """Test cases for Ccds model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.ccds import Ccds

        return {c.name: c for c in inspect(Ccds).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.ccds import Ccds

        assert Ccds.__tablename__ == "ccds"

    def test_is_declarative_base_subclass(self) -> None:
        from genew4_orm.models.ccds import Ccds

        assert issubclass(Ccds, DeclarativeBase)

    def test_has_12_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 12

    def test_chrom_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_chrom" in columns
        assert isinstance(columns["ccds_chrom"].type, String)

    def test_acc_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_acc" in columns

    def test_sym_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_sym" in columns

    def test_eg_id_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_eg_id" in columns

    def test_id_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_id" in columns

    def test_status_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_status" in columns

    def test_strand_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_strand" in columns

    def test_from_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_from" in columns

    def test_to_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_to" in columns

    def test_locations_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_locations" in columns
        assert isinstance(columns["ccds_locations"].type, Text)

    def test_match_type_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_match_type" in columns

    def test_hgnc_id_column(self, columns: dict[str, Column]) -> None:
        assert "ccds_hgnc_id" in columns
        assert isinstance(columns["ccds_hgnc_id"].type, Integer)


class TestCcdsSequence:
    """Test cases for CcdsSequence model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.ccds_sequence import CcdsSequence

        return {c.name: c for c in inspect(CcdsSequence).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.ccds_sequence import CcdsSequence

        assert CcdsSequence.__tablename__ == "ccds_seq"

    def test_has_4_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 4

    def test_ccds_id_column(self, columns: dict[str, Column]) -> None:
        assert "ccdseq_ccds_id" in columns

    def test_build_column(self, columns: dict[str, Column]) -> None:
        assert "ccdseq_build" in columns

    def test_chrom_column(self, columns: dict[str, Column]) -> None:
        assert "ccdseq_chrom" in columns

    def test_seq_column(self, columns: dict[str, Column]) -> None:
        assert "ccdseq_seq" in columns
        assert isinstance(columns["ccdseq_seq"].type, Text)


class TestGene2Refseq:
    """Test cases for Gene2Refseq model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.gene2refseq import Gene2Refseq

        return {c.name: c for c in inspect(Gene2Refseq).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.gene2refseq import Gene2Refseq

        assert Gene2Refseq.__tablename__ == "gene2refseq"

    def test_has_16_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 16

    def test_key_columns_exist(self, columns: dict[str, Column]) -> None:
        expected = [
            "g2r_tax_id",
            "g2r_eg_id",
            "g2r_status",
            "g2r_rna_nt_acc_ver",
            "g2r_rna_nt_gi",
            "g2r_prot_acc_ver",
            "g2r_prot_gi",
            "g2r_gen_nt_acc_ver",
            "g2r_gen_nt_gi",
            "g2r_start_pos_gen_acc",
            "g2r_end_pos_gen_acc",
            "g2r_orientation",
            "g2r_assembly",
            "g2r_mat_pept_acc_ver",
            "g2r_mat_pept_gi",
            "g2r_symbol",
        ]
        for col_name in expected:
            assert col_name in columns, f"Missing column: {col_name}"


class TestGeneInfo:
    """Test cases for GeneInfo model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.gene_info import GeneInfo

        return {c.name: c for c in inspect(GeneInfo).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.gene_info import GeneInfo

        assert GeneInfo.__tablename__ == "gene_info"

    def test_has_16_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 16

    def test_key_columns_exist(self, columns: dict[str, Column]) -> None:
        expected = [
            "gi_tax_id",
            "gi_eg_id",
            "gi_sym",
            "gi_locustag",
            "gi_synonyms",
            "gi_dbxrefs",
            "gi_chrom",
            "gi_map_location",
            "gi_description",
            "gi_type_of_gene",
            "gi_sym_from_nome_auth",
            "gi_full_name_from_nome_auth",
            "gi_nome_status",
            "gi_other_designations",
            "gi_modification_date",
            "gi_hgnc_id",
        ]
        for col_name in expected:
            assert col_name in columns, f"Missing column: {col_name}"


class TestPseudogeneOrg:
    """Test cases for PseudogeneOrg model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.pseudogene_org import PseudogeneOrg

        return {c.name: c for c in inspect(PseudogeneOrg).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.pseudogene_org import PseudogeneOrg

        assert PseudogeneOrg.__tablename__ == "pseudogene_org"

    def test_has_9_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 9

    def test_id_is_pk(self, columns: dict[str, Column]) -> None:
        assert columns["porg_id"].primary_key is True
        assert isinstance(columns["porg_id"].type, Integer)

    def test_all_columns_exist(self, columns: dict[str, Column]) -> None:
        expected = [
            "porg_id",
            "porg_chr",
            "porg_strand",
            "porg_start",
            "porg_end",
            "porg_seq",
            "porg_class",
            "porg_link",
            "porg_parent_gene",
        ]
        for col_name in expected:
            assert col_name in columns, f"Missing column: {col_name}"


class TestOtterSequence:
    """Test cases for OtterSequence model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.otter_sequence import OtterSequence

        return {c.name: c for c in inspect(OtterSequence).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.otter_sequence import OtterSequence

        assert OtterSequence.__tablename__ == "otter_seq"

    def test_has_4_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 4

    def test_all_columns_exist(self, columns: dict[str, Column]) -> None:
        for col_name in ["oseq_gene_id", "oseq_defline", "oseq_seq", "oseq_length"]:
            assert col_name in columns

    def test_gene_id_not_nullable(self, columns: dict[str, Column]) -> None:
        assert columns["oseq_gene_id"].nullable is False


class TestEnsemblSequence:
    """Test cases for EnsemblSequence model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.ensembl_sequence import EnsemblSequence

        return {c.name: c for c in inspect(EnsemblSequence).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.ensembl_sequence import EnsemblSequence

        assert EnsemblSequence.__tablename__ == "ensembl_seq"

    def test_has_6_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 6

    def test_all_columns_exist(self, columns: dict[str, Column]) -> None:
        for col_name in [
            "eseq_source",
            "eseq_defline",
            "eseq_ensembl_gene_id",
            "eseq_ensembl_transcript_id",
            "eseq_seq",
            "eseq_length",
        ]:
            assert col_name in columns

    def test_length_is_integer(self, columns: dict[str, Column]) -> None:
        assert isinstance(columns["eseq_length"].type, Integer)


class TestHseq:
    """Test cases for Hseq model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.hseq import Hseq

        return {c.name: c for c in inspect(Hseq).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.hseq import Hseq

        assert Hseq.__tablename__ == "hseq"

    def test_has_13_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 13

    def test_id_is_auto_pk(self, columns: dict[str, Column]) -> None:
        col = columns["hseq_id"]
        assert col.primary_key is True
        assert isinstance(col.type, Integer)
        assert col.autoincrement in (True, "auto")

    def test_all_columns_exist(self, columns: dict[str, Column]) -> None:
        expected = [
            "hseq_id",
            "hseq_ext",
            "hseq_editor",
            "hseq_molecule",
            "hseq_submitted",
            "hseq_status",
            "hseq_priority",
            "hseq_run_notes",
            "hseq_comment",
            "hseq_entry_class",
            "hseq_isnew",
            "hseq_defline",
            "hseq_seq",
        ]
        for col_name in expected:
            assert col_name in columns, f"Missing column: {col_name}"


class TestHgncId2CcdsId:
    """Test cases for HgncId2CcdsId model."""

    @pytest.fixture()
    def columns(self) -> dict[str, Column]:
        from genew4_orm.models.hgnc_id2ccds_id import HgncId2CcdsId

        return {c.name: c for c in inspect(HgncId2CcdsId).columns}

    def test_tablename(self) -> None:
        from genew4_orm.models.hgnc_id2ccds_id import HgncId2CcdsId

        assert HgncId2CcdsId.__tablename__ == "hgnc_id2ccds_id"

    def test_has_2_columns(self, columns: dict[str, Column]) -> None:
        assert len(columns) == 2

    def test_hgnc_id_column(self, columns: dict[str, Column]) -> None:
        assert "hgnc_id2ccds_id_hgnc_id" in columns
        assert isinstance(columns["hgnc_id2ccds_id_hgnc_id"].type, Integer)

    def test_ccds_id_column(self, columns: dict[str, Column]) -> None:
        assert "hgnc_id2ccds_id_ccds_id" in columns
        assert hasattr(columns["hgnc_id2ccds_id_ccds_id"].type, "length")
