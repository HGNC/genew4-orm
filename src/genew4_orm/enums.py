"""Database enum definitions matching TypeScript ORM.

All enums are string-based for PostgreSQL compatibility and match
the exact values from the hgnc-tools-api TypeScript implementation.
"""

from enum import StrEnum
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field


def enum_field(
    enum_class: type[StrEnum],
    *,
    default: Any | None = None,
    nullable: bool = False,
    column_name: str | None = None,
) -> Any:
    """Create a SQLModel Field with proper PostgreSQL Enum column configuration.

    This helper creates a SQLModel Field with a SQLAlchemy Enum column
    properly configured for PostgreSQL compatibility.

    Args:
        enum_class: The StrEnum class to use for this field.
        default: Default value for the field (typically from the enum).
        nullable: Whether the field allows NULL values.
        column_name: Optional custom column name (defaults to model field name).

    Returns:
        A SQLModel Field configured with an Enum column.

    Example:
        >>> class Gene(SQLModel, table=True):
        ...     locus_type: GeneLocusType = enum_field(
        ...         GeneLocusType,
        ...         default=GeneLocusType.UNDEF,
        ...         nullable=False
        ...     )
    """
    sa_column_kwargs: dict[str, Any] = {}
    if column_name is not None:
        sa_column_kwargs["name"] = column_name

    return Field(
        default=default,
        sa_column=Column(
            SQLEnum(enum_class, create_constraint=True, native_enum=False),
            nullable=nullable,
            **sa_column_kwargs,
        ),
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


# Export all enums for easy importing
__all__ = [
    "GeneLocusType",
    "GeneStatus",
    "GeneGroupStatus",
    "GeneGroupType",
    "Grch38SourceType",
    "Grch38MarkType",
    "CytobandSourceType",
    "enum_field",
]
