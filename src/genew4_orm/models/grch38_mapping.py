"""Grch38Mapping model representing the coord_match_grch38 table.

This model contains GRCh38 coordinate mapping data with composite primary key.
"""

from sqlalchemy import Column, Integer, String
from sqlmodel import Field, SQLModel

from genew4_orm.enums import Grch38MarkType, Grch38SourceType


class Grch38Mapping(SQLModel, table=True):
    """Grch38Mapping entity representing the coord_match_grch38 table.

    Genomic coordinate mappings to GRCh38 with composite primary key.
    Note: This table uses all columns as part of the primary key
    (no auto-incrementing ID).
    """

    __tablename__ = "coord_match_grch38"

    # Composite primary key fields
    source: Grch38SourceType = Field(
        sa_column=Column("cm_source", String, primary_key=True),
        description="Data source (NCBI, Ensembl, Chrom, HGNC)",
    )
    strand: str = Field(
        max_length=1,
        sa_column=Column("cm_strand", String, primary_key=True),
        description="Strand orientation (+ or -)",
    )
    chromosome: str = Field(
        max_length=255,
        sa_column=Column("cm_chr", String, primary_key=True),
        description="Chromosome name",
    )
    start: int = Field(
        sa_column=Column("cm_start", Integer, primary_key=True),
        description="Start position",
    )
    end: int = Field(
        sa_column=Column("cm_end", Integer, primary_key=True),
        description="End position",
    )
    map_by: str = Field(
        sa_column=Column("cm_mapby", String, primary_key=True),
        description="Mapping method/reference",
    )

    # Additional optional fields (not part of primary key)
    source_id: str | None = Field(
        default=None,
        max_length=100,
        sa_column=Column("cm_source_id", String),
        description="Source identifier",
    )
    ncbi_gene_id: int | None = Field(
        default=None,
        sa_column=Column("cm_eg_id", Integer),
        description="NCBI Gene ID",
    )
    hgnc_id: int | None = Field(
        default=None,
        sa_column=Column("cm_hgnc_id", Integer),
        description="HGNC Gene ID",
    )
    notes: str | None = Field(
        default=None,
        sa_column=Column("cm_notes", String),
        description="Additional notes",
    )
    mark: Grch38MarkType | None = Field(
        default=None,
        sa_column=Column("cm_mark", String),
        description="Mark type (max or hidden)",
    )

    def __repr__(self) -> str:
        """Return string representation of Grch38Mapping."""
        return (
            f"<Grch38Mapping(source={self.source}, chromosome='{self.chromosome}', start={self.start}, end={self.end})>"
        )
