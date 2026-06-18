"""Ccds model for the ccds table.

Used by coord-builder (CCDS sub-source), xref-loader (CCDS loader + post-load),
and hseq-importer (CCDS source).
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Ccds(DeclarativeBase):
    """CCDS (Consensus Coding Sequence) record.

    Stores CCDS identifier mappings, chromosomal coordinates,
    and match status for cross-reference with HGNC genes.
    """

    __tablename__ = "ccds"

    ccds_id: Mapped[str | None] = mapped_column(
        "ccds_id",
        String(50),
        primary_key=True, nullable=False,
        comment="CCDS identifier (primary key)",
    )
    chromosome: Mapped[str | None] = mapped_column(
        "ccds_chrom",
        String(50),
        comment="Chromosome",
    )
    accession: Mapped[str | None] = mapped_column(
        "ccds_acc",
        String(50),
        comment="CCDS accession",
    )
    symbol: Mapped[str | None] = mapped_column(
        "ccds_sym",
        String(255),
        comment="Gene symbol",
    )
    ncbi_gene_id: Mapped[str | None] = mapped_column(
        "ccds_eg_id",
        String(50),
        comment="NCBI Entrez Gene ID",
    )
    status: Mapped[str | None] = mapped_column(
        "ccds_status",
        String(100),
        comment="CCDS status (Public, Withdrawn, etc.)",
    )
    strand: Mapped[str | None] = mapped_column(
        "ccds_strand",
        String(5),
        comment="Strand (+/-)",
    )
    start: Mapped[str | None] = mapped_column(
        "ccds_from",
        String(50),
        comment="Start coordinate",
    )
    end: Mapped[str | None] = mapped_column(
        "ccds_to",
        String(50),
        comment="End coordinate",
    )
    locations: Mapped[str | None] = mapped_column(
        "ccds_locations",
        Text,
        comment="Location information",
    )
    match_type: Mapped[str | None] = mapped_column(
        "ccds_match_type",
        String(100),
        comment="Match type classification",
    )
    hgnc_id: Mapped[int | None] = mapped_column(
        "ccds_hgnc_id",
        Integer,
        comment="HGNC ID (back-filled post-load)",
    )
