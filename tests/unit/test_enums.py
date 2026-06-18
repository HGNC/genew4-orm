"""Unit tests for enums module."""

from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from genew4_orm.enums import (
    CytobandSourceType,
    GeneGroupStatus,
    GeneGroupType,
    GeneLocusType,
    GeneStatus,
    Grch38MarkType,
    Grch38SourceType,
    PublishStatus,
    enum_field,
)


def _build_enum_model(**field_kwargs: Any) -> type:
    """Build an isolated DeclarativeBase model exposing one ``enum_field`` column.

    A fresh ``declarative_base()`` (own registry/metadata) is created per call so
    each test gets an isolated namespace — no shared-metadata table-name
    collisions and no subclassing ``DeclarativeBase`` directly (which SQLAlchemy
    rejects).
    """

    base = declarative_base()

    class _EnumModel(base):
        __tablename__ = "test_enum_field_model"

        id: Mapped[int] = mapped_column(primary_key=True)
        status: Mapped[PublishStatus] = enum_field(PublishStatus, **field_kwargs)

    return _EnumModel


class TestEnumField:
    """Test cases for enum_field function."""

    def test_enum_field_basic(self) -> None:
        """Test enum_field creates an Enum column with the enum class."""
        model = _build_enum_model(default=PublishStatus.PENDING, nullable=False)
        col = inspect(model).columns["status"]

        assert isinstance(col.type, SAEnum)
        assert col.type.enum_class is PublishStatus
        assert col.default is not None
        assert col.default.arg is PublishStatus.PENDING

    def test_enum_field_with_default_none(self) -> None:
        """Test enum_field with None default."""
        model = _build_enum_model(default=None, nullable=True)
        col = inspect(model).columns["status"]

        assert col.default is None
        assert col.nullable is True

    def test_enum_field_nullable_false(self) -> None:
        """Test enum_field with nullable=False."""
        model = _build_enum_model(default=PublishStatus.PENDING, nullable=False)
        col = inspect(model).columns["status"]

        assert col.nullable is False

    def test_enum_field_nullable_true(self) -> None:
        """Test enum_field with nullable=True."""
        model = _build_enum_model(default=None, nullable=True)
        col = inspect(model).columns["status"]

        assert col.nullable is True

    def test_enum_field_with_column_name(self) -> None:
        """Test enum_field with custom column_name."""
        model = _build_enum_model(
            default=PublishStatus.PENDING,
            nullable=False,
            column_name="custom_status_column",
        )
        columns = {c.name: c for c in inspect(model).columns}

        assert "custom_status_column" in columns
        assert isinstance(columns["custom_status_column"].type, SAEnum)

    def test_enum_field_in_model(self) -> None:
        """Test enum_field within a DeclarativeBase model yields an Enum column."""
        base = declarative_base()

        class TestModel(base):
            __tablename__ = "test_model"

            id: Mapped[int] = mapped_column(primary_key=True)
            status: Mapped[PublishStatus] = enum_field(
                PublishStatus,
                default=PublishStatus.PENDING,
                nullable=False,
                column_name="status",
            )

        assert TestModel.__tablename__ == "test_model"
        col = inspect(TestModel).columns["status"]
        assert isinstance(col.type, SAEnum)
        assert col.type.enum_class is PublishStatus
        assert col.type.create_constraint is True
        assert col.type.native_enum is False


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


class TestPublishStatus:
    """Test cases for PublishStatus enum."""

    def test_publish_status_values(self) -> None:
        """Test PublishStatus has expected values."""
        assert PublishStatus.PENDING == "pending"
        assert PublishStatus.PUBLISHED == "published"
        assert PublishStatus.REJECTED == "rejected"

    def test_publish_status_str_method(self) -> None:
        """Test PublishStatus __str__ method returns value."""
        assert str(PublishStatus.PENDING) == "pending"
        assert str(PublishStatus.PUBLISHED) == "published"
        assert str(PublishStatus.REJECTED) == "rejected"

    def test_publish_status_all_values_exist(self) -> None:
        """Test that all 3 PublishStatus values exist."""
        assert len(PublishStatus) == 3


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

    def test_iterate_publish_status(self) -> None:
        """Test iterating over PublishStatus values."""
        values = list(PublishStatus)
        assert len(values) == 3
        assert PublishStatus.PENDING in values
        assert PublishStatus.PUBLISHED in values
        assert PublishStatus.REJECTED in values
