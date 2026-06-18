"""Grch38Mapping model representing the coord_match_grch38 table.

This model contains GRCh38 coordinate mapping data with composite primary key.
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from genew4_orm.enums import Grch38MarkType, Grch38SourceType


class Grch38Mapping(DeclarativeBase):
    """Grch38Mapping entity representing the coord_match_grch38 table.

    Genomic coordinate mappings to GRCh38 with composite primary key.
    Note: This table uses all columns as part of the primary key
    (no auto-incrementing ID). The enum-typed fields map to plain ``String``
    columns in the database (matching the legacy SQLModel ``sa_column``).
    """

    __tablename__ = "coord_match_grch38"

    # Composite primary key fields
    source: Mapped[Grch38SourceType] = mapped_column(
        "cm_source", String, primary_key=True, nullable=False, comment="Data source (NCBI, Ensembl, Chrom, HGNC)"
    )
    strand: Mapped[str] = mapped_column(
        "cm_strand", String, primary_key=True, nullable=False, comment="Strand orientation (+ or -)"
    )
    chromosome: Mapped[str] = mapped_column(
        "cm_chr", String, primary_key=True, nullable=False, comment="Chromosome name"
    )
    start: Mapped[int] = mapped_column("cm_start", Integer, primary_key=True, nullable=False, comment="Start position")
    end: Mapped[int] = mapped_column("cm_end", Integer, primary_key=True, nullable=False, comment="End position")
    map_by: Mapped[str] = mapped_column(
        "cm_mapby", String, primary_key=True, nullable=False, comment="Mapping method/reference"
    )

    # Additional optional fields (not part of primary key)
    source_id: Mapped[str | None] = mapped_column(
        "cm_source_id", String, comment="Source identifier"
    )
    ncbi_gene_id: Mapped[int | None] = mapped_column("cm_eg_id", Integer, comment="NCBI Gene ID")
    hgnc_id: Mapped[int | None] = mapped_column("cm_hgnc_id", Integer, comment="HGNC Gene ID")
    notes: Mapped[str | None] = mapped_column("cm_notes", String, comment="Additional notes")
    mark: Mapped[Grch38MarkType | None] = mapped_column(
        "cm_mark", String, default=None, comment="Mark type (max or hidden)"
    )

    def __repr__(self) -> str:
        """Return string representation of Grch38Mapping."""
        return (
            f"<Grch38Mapping(source={self.source}, chromosome='{self.chromosome}', start={self.start}, end={self.end})>"
        )
