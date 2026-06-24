"""Database enum definitions matching TypeScript ORM.

All enums are string-based for PostgreSQL compatibility and match
the exact values from the hgnc-tools-api TypeScript implementation.
"""

from enum import StrEnum
from typing import Any

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import mapped_column


def enum_field(
    enum_class: type[StrEnum],
    *,
    default: Any | None = None,
    nullable: bool = False,
    column_name: str | None = None,
) -> Any:
    """Create a plain SQLAlchemy column spec for an enum-backed ``mapped_column``.

    Returns a :func:`sqlalchemy.orm.mapped_column` configured with an
    ``Enum(enum_class, create_constraint=True, native_enum=False)`` column type,
    suitable as the right-hand side of an annotated attribute on a
    :class:`db_common.DeclarativeBase` subclass. This is the plain-SQLAlchemy
    replacement for the former SQLAlchemy-1.x/SQLModel
    ``Field(..., sa_column=Column(Enum(...)))`` wrapper; the call signature is
    unchanged so the only caller (``Comment.status``) keeps working.

    Args:
        enum_class: The StrEnum class to use for this field.
        default: Default value for the field (typically from the enum).
        nullable: Whether the field allows NULL values.
        column_name: Optional custom column name (defaults to model field name).

    Returns:
        A ``mapped_column`` instance (a ``MappedColumn``) usable directly as the
        value of an annotated attribute, e.g. ``status: Mapped[...] = enum_field(...)``.

    Example:
        >>> class Comment(DeclarativeBase):
        ...     __tablename__ = "comment"
        ...     status: Mapped[PublishStatus] = enum_field(
        ...         PublishStatus,
        ...         default=PublishStatus.PENDING,
        ...         nullable=False,
        ...         column_name="status",
        ...     )
    """
    kwargs: dict[str, Any] = {"default": default, "nullable": nullable}
    if column_name is not None:
        kwargs["name"] = column_name
    return mapped_column(
        # values_callable persists the StrEnum *value* (e.g. 'internal',
        # 'pending') rather than the member NAME ('INTERNAL', 'PENDING'), which
        # is SQLAlchemy's default. This keeps the stored bytes, the generated
        # CHECK constraint, and docs/models.md in agreement — and matches the
        # real family_new / comment columns mirrored from the TypeScript ORM.
        SQLEnum(
            enum_class,
            create_constraint=True,
            native_enum=False,
            values_callable=lambda klass: [member.value for member in klass],
        ),
        **kwargs,
    )


class GeneLocusType(StrEnum):
    """Gene locus type classification (38 values).

    Represents the type of gene or genomic region based on HGNC classifications.
    """

    COMPLEX_LOCUS_CONSTITUENT = "complex locus constituent"
    ENDOGENOUS_RETROVIRUS = "endogenous retrovirus"
    FRAGILE_SITE = "fragile site"
    GWPP = "gene with protein product"
    GWPP_DEMONSTRATES_SOMATIC_REARRANGEMENT = "gene with protein product, demonstrates somatic rearrangement"
    GWPP_FUNCTION_KNOWN_OR_INFERRED = "gene with protein product, function known or inferred"
    GWPP_FUNCTION_UNKNOWN = "gene with protein product, function unknown"
    GWPP_INFERRED = "gene with protein product, inferred"
    IMMUNOGLOBULIN_GENE = "immunoglobulin gene"
    IMMUNOGLOBULIN_PSEUDOGENE = "immunoglobulin pseudogene"
    NON_HUMAN_ORTHOLOG = "non-human ortholog"
    PHENOTYPE_ONLY = "phenotype only"
    PROTOCADHERIN = "protocadherin"
    PSEUDOGENE = "pseudogene"
    PSEUDOGENE_TRANSCRIBED = "pseudogene, transcribed"
    READ_THROUGH_TRANSCRIPT = "read-through transcript"
    REGION = "region"
    RNA_CLUSTER = "RNA, cluster"
    RNA_LONG_NON_CODING = "RNA, long non-coding"
    RNA_MICRO = "RNA, micro"
    RNA_MISC = "RNA, misc"
    RNA_PSEUDOGENE = "RNA, pseudogene"
    RNA_RIBOSOMAL = "RNA, ribosomal"
    RNA_SMALL_NUCLEAR = "RNA, small nuclear"
    RNA_SMALL_NUCLEOLAR = "RNA, small nucleolar"
    RNA_TRANSFER = "RNA, transfer"
    RNA_VAULT = "RNA, vault"
    RNA_Y = "RNA, Y"
    T_CELL_RECEPTOR_GENE = "T cell receptor gene"
    T_CELL_RECEPTOR_PSEUDOGENE = "T cell receptor pseudogene"
    TRANSPOSABLE_ELEMENT = "transposable element"
    UNDEF = "undef"
    UNKNOWN = "unknown"
    VIRUS_INTEGRATION_SITE = "virus integration site"

    def __str__(self) -> str:
        return self.value


class GeneStatus(StrEnum):
    """Gene approval and status classification (8 values).

    Represents the current status of a gene symbol in the HGNC database.
    """

    APPROVED = "Approved"
    PENDING = "Pending"
    RESERVED = "Reserved"
    RESERVED_NON_HUMAN = "Reserved Non-human"
    SUSPENDED = "Suspended"
    DELETE = "Delete"
    ENTRY_WITHDRAWN = "Entry Withdrawn"
    SYMBOL_WITHDRAWN = "Symbol Withdrawn"

    def __str__(self) -> str:
        return self.value


class GeneGroupStatus(StrEnum):
    """Gene group visibility status (3 values).

    Controls whether a gene group is visible internally, exported publicly,
    or marked for deletion.
    """

    DELETE = "delete"
    EXPORTED = "exported"
    INTERNAL = "internal"

    def __str__(self) -> str:
        return self.value


class GeneGroupType(StrEnum):
    """Gene group type classification (1 value).

    Currently only 'set' type is supported, but may be extended in the future.
    """

    SET = "set"

    def __str__(self) -> str:
        return self.value


class Grch38SourceType(StrEnum):
    """GRCh38 coordinate mapping data source (4 values).

    Identifies the source of genomic coordinate mappings.
    """

    NCBI = "NCBI"
    ENSEMBL = "Ensembl"
    CHROM = "Chrom"
    HGNC = "HGNC"

    def __str__(self) -> str:
        return self.value


class Grch38MarkType(StrEnum):
    """GRCh38 coordinate marking type (2 values).

    Controls how coordinate mappings are displayed or processed.
    """

    MAX = "max"
    HIDDEN = "hidden"

    def __str__(self) -> str:
        return self.value


class CytobandSourceType(StrEnum):
    """Cytogenetic band data source (2 values).

    Identifies the source of cytoband coordinate data.
    """

    UCSC = "UCSC"
    ENSEMBL = "Ensembl"

    def __str__(self) -> str:
        return self.value


class PublishStatus(StrEnum):
    """Comment publication status (3 values).

    Controls the visibility/state of a comment in the publication workflow.
    """

    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return self.value


# Export all enums for easy importing
__all__ = [
    "GeneLocusType",
    "GeneStatus",
    "GeneGroupStatus",
    "GeneGroupType",
    "Grch38SourceType",
    "Grch38MarkType",
    "CytobandSourceType",
    "PublishStatus",
    "enum_field",
]
