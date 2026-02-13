"""Unit tests for enums module."""

from sqlmodel import Field, SQLModel

from genew4_orm.enums import (
    CytobandSourceType,
    GeneGroupStatus,
    GeneGroupType,
    GeneLocusType,
    GeneStatus,
    Grch38MarkType,
    Grch38SourceType,
    enum_field,
)


class TestEnumField:
    """Test cases for enum_field function."""

    def test_enum_field_basic(self) -> None:
        """Test enum_field creates a proper Field."""
        field = enum_field(GeneStatus, default=GeneStatus.APPROVED, nullable=False)

        assert field is not None
        assert field.default is GeneStatus.APPROVED

    def test_enum_field_with_default_none(self) -> None:
        """Test enum_field with None default."""
        field = enum_field(GeneStatus, default=None, nullable=True)

        assert field is not None

    def test_enum_field_nullable_false(self) -> None:
        """Test enum_field with nullable=False."""
        field = enum_field(GeneStatus, default=GeneStatus.APPROVED, nullable=False)

        assert field is not None

    def test_enum_field_nullable_true(self) -> None:
        """Test enum_field with nullable=True."""
        field = enum_field(GeneStatus, default=None, nullable=True)

        assert field is not None

    def test_enum_field_with_column_name(self) -> None:
        """Test enum_field with custom column_name."""
        field = enum_field(
            GeneStatus,
            default=GeneStatus.APPROVED,
            nullable=False,
            column_name="custom_status_column",
        )

        assert field is not None
        # The column name should be set in sa_column_kwargs

    def test_enum_field_in_model(self) -> None:
        """Test enum_field within a SQLModel."""

        class TestModel(SQLModel, table=True):
            __tablename__ = "test_model"

            id: int | None = Field(default=None, primary_key=True)
            status: GeneStatus = enum_field(
                GeneStatus,
                default=GeneStatus.APPROVED,
                nullable=False,
            )

        # Model should be created successfully
        assert TestModel.__tablename__ == "test_model"
        assert hasattr(TestModel, "status")


class TestGeneLocusType:
    """Test cases for GeneLocusType enum."""

    def test_gene_locus_type_values(self) -> None:
        """Test GeneLocusType has expected values."""
        assert GeneLocusType.GWPP == "gene with protein product"
        assert GeneLocusType.PSEUDOGENE == "pseudogene"
        assert GeneLocusType.UNDEF == "undef"
        assert GeneLocusType.UNKNOWN == "unknown"
        assert GeneLocusType.RNA_MICRO == "RNA, micro"
        assert GeneLocusType.COMPLEX_LOCUS_CONSTITUENT == "complex locus constituent"

    def test_gene_locus_type_str_method(self) -> None:
        """Test GeneLocusType __str__ method returns value."""
        assert str(GeneLocusType.GWPP) == "gene with protein product"
        assert str(GeneLocusType.PSEUDOGENE) == "pseudogene"
        assert str(GeneLocusType.UNDEF) == "undef"

    def test_gene_locus_type_all_values_exist(self) -> None:
        """Test that GeneLocusType values exist."""
        # Count actual values - there are 34 values
        actual_count = len(GeneLocusType)
        assert actual_count >= 30  # At least 30 values exist


class TestGeneStatus:
    """Test cases for GeneStatus enum."""

    def test_gene_status_values(self) -> None:
        """Test GeneStatus has expected values."""
        assert GeneStatus.APPROVED == "Approved"
        assert GeneStatus.PENDING == "Pending"
        assert GeneStatus.RESERVED == "Reserved"
        assert GeneStatus.DELETE == "Delete"
        assert GeneStatus.ENTRY_WITHDRAWN == "Entry Withdrawn"

    def test_gene_status_str_method(self) -> None:
        """Test GeneStatus __str__ method returns value."""
        assert str(GeneStatus.APPROVED) == "Approved"
        assert str(GeneStatus.PENDING) == "Pending"
        assert str(GeneStatus.DELETE) == "Delete"

    def test_gene_status_all_values_exist(self) -> None:
        """Test that all 8 GeneStatus values exist."""
        expected_count = 8
        actual_count = len(GeneStatus)
        assert actual_count == expected_count


class TestGeneGroupStatus:
    """Test cases for GeneGroupStatus enum."""

    def test_gene_group_status_values(self) -> None:
        """Test GeneGroupStatus has expected values."""
        assert GeneGroupStatus.DELETE == "delete"
        assert GeneGroupStatus.EXPORTED == "exported"
        assert GeneGroupStatus.INTERNAL == "internal"

    def test_gene_group_status_str_method(self) -> None:
        """Test GeneGroupStatus __str__ method returns value."""
        assert str(GeneGroupStatus.DELETE) == "delete"
        assert str(GeneGroupStatus.EXPORTED) == "exported"
        assert str(GeneGroupStatus.INTERNAL) == "internal"

    def test_gene_group_status_all_values_exist(self) -> None:
        """Test that all 3 GeneGroupStatus values exist."""
        expected_count = 3
        actual_count = len(GeneGroupStatus)
        assert actual_count == expected_count


class TestGeneGroupType:
    """Test cases for GeneGroupType enum."""

    def test_gene_group_type_values(self) -> None:
        """Test GeneGroupType has expected values."""
        assert GeneGroupType.SET == "set"

    def test_gene_group_type_str_method(self) -> None:
        """Test GeneGroupType __str__ method returns value."""
        assert str(GeneGroupType.SET) == "set"

    def test_gene_group_type_all_values_exist(self) -> None:
        """Test that at least 1 GeneGroupType value exists."""
        assert len(GeneGroupType) >= 1


class TestGrch38SourceType:
    """Test cases for Grch38SourceType enum."""

    def test_grch38_source_type_values(self) -> None:
        """Test Grch38SourceType has expected values."""
        assert Grch38SourceType.NCBI == "NCBI"
        assert Grch38SourceType.ENSEMBL == "Ensembl"
        assert Grch38SourceType.CHROM == "Chrom"
        assert Grch38SourceType.HGNC == "HGNC"

    def test_grch38_source_type_str_method(self) -> None:
        """Test Grch38SourceType __str__ method returns value."""
        assert str(Grch38SourceType.NCBI) == "NCBI"
        assert str(Grch38SourceType.ENSEMBL) == "Ensembl"
        assert str(Grch38SourceType.CHROM) == "Chrom"
        assert str(Grch38SourceType.HGNC) == "HGNC"

    def test_grch38_source_type_all_values_exist(self) -> None:
        """Test that all 4 Grch38SourceType values exist."""
        expected_count = 4
        actual_count = len(Grch38SourceType)
        assert actual_count == expected_count


class TestGrch38MarkType:
    """Test cases for Grch38MarkType enum."""

    def test_grch38_mark_type_values(self) -> None:
        """Test Grch38MarkType has expected values."""
        assert Grch38MarkType.MAX == "max"
        assert Grch38MarkType.HIDDEN == "hidden"

    def test_grch38_mark_type_str_method(self) -> None:
        """Test Grch38MarkType __str__ method returns value."""
        assert str(Grch38MarkType.MAX) == "max"
        assert str(Grch38MarkType.HIDDEN) == "hidden"

    def test_grch38_mark_type_all_values_exist(self) -> None:
        """Test that all 2 Grch38MarkType values exist."""
        expected_count = 2
        actual_count = len(Grch38MarkType)
        assert actual_count == expected_count


class TestCytobandSourceType:
    """Test cases for CytobandSourceType enum."""

    def test_cytoband_source_type_values(self) -> None:
        """Test CytobandSourceType has expected values."""
        assert CytobandSourceType.UCSC == "UCSC"
        assert CytobandSourceType.ENSEMBL == "Ensembl"

    def test_cytoband_source_type_str_method(self) -> None:
        """Test CytobandSourceType __str__ method returns value."""
        assert str(CytobandSourceType.UCSC) == "UCSC"
        assert str(CytobandSourceType.ENSEMBL) == "Ensembl"

    def test_cytoband_source_type_all_values_exist(self) -> None:
        """Test that all 2 CytobandSourceType values exist."""
        expected_count = 2
        actual_count = len(CytobandSourceType)
        assert actual_count == expected_count


class TestEnumStringComparison:
    """Test cases for enum string comparison."""

    def test_enum_equals_string(self) -> None:
        """Test that enum value equals its string representation."""
        assert GeneStatus.APPROVED == "Approved"
        assert GeneStatus.PENDING == "Pending"

    def test_enum_in_string_list(self) -> None:
        """Test that enum value can be checked in string list."""
        statuses = ["Approved", "Pending", "Reserved"]
        assert GeneStatus.APPROVED in statuses
        assert GeneStatus.PENDING in statuses


class TestEnumIteration:
    """Test cases for enum iteration."""

    def test_iterate_gene_locus_type(self) -> None:
        """Test iterating over GeneLocusType values."""
        values = list(GeneLocusType)
        assert len(values) >= 30
        assert GeneLocusType.GWPP in values
        assert GeneLocusType.PSEUDOGENE in values

    def test_iterate_gene_status(self) -> None:
        """Test iterating over GeneStatus values."""
        values = list(GeneStatus)
        assert len(values) == 8
        assert GeneStatus.APPROVED in values
        assert GeneStatus.DELETE in values
