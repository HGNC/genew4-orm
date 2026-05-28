"""Ccds model for the ccds table.

Used by coord-builder (CCDS sub-source), xref-loader (CCDS loader + post-load),
and hseq-importer (CCDS source).
"""

from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field, SQLModel


class Ccds(SQLModel, table=True):
    """CCDS (Consensus Coding Sequence) record.

    Stores CCDS identifier mappings, chromosomal coordinates,
    and match status for cross-reference with HGNC genes.
    """

    __tablename__ = "ccds"

    ccds_id: str | None = Field(
        default=None,
        primary_key=True,
        max_length=50,
        description="CCDS identifier (primary key)",
    )
    chromosome: str | None = Field(
        default=None,
        sa_column=Column("ccds_chrom", String(50)),
        description="Chromosome",
    )
    accession: str | None = Field(
        default=None,
        sa_column=Column("ccds_acc", String(50)),
        description="CCDS accession",
    )
    symbol: str | None = Field(
        default=None,
        sa_column=Column("ccds_sym", String(255)),
        description="Gene symbol",
    )
    ncbi_gene_id: str | None = Field(
        default=None,
        sa_column=Column("ccds_eg_id", String(50)),
        description="NCBI Entrez Gene ID",
    )
    status: str | None = Field(
        default=None,
        sa_column=Column("ccds_status", String(100)),
        description="CCDS status (Public, Withdrawn, etc.)",
    )
    strand: str | None = Field(
        default=None,
        sa_column=Column("ccds_strand", String(5)),
        description="Strand (+/-)",
    )
    start: str | None = Field(
        default=None,
        sa_column=Column("ccds_from", String(50)),
        description="Start coordinate",
    )
    end: str | None = Field(
        default=None,
        sa_column=Column("ccds_to", String(50)),
        description="End coordinate",
    )
    locations: str | None = Field(
        default=None,
        sa_column=Column("ccds_locations", Text),
        description="Location information",
    )
    match_type: str | None = Field(
        default=None,
        sa_column=Column("ccds_match_type", String(100)),
        description="Match type classification",
    )
    hgnc_id: int | None = Field(
        default=None,
        sa_column=Column("ccds_hgnc_id", Integer),
        description="HGNC ID (back-filled post-load)",
    )
