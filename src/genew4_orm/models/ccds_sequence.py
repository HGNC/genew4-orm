"""CcdsSequence model for the ccds_seq table.

Used by hseq-importer (CCDS source sequence lookup).
"""

from db_common import DeclarativeBase
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


class CcdsSequence(DeclarativeBase):
    """CCDS sequence record.

    Stores the nucleotide sequence associated with a CCDS identifier,
    along with build and chromosome metadata.
    """

    __tablename__ = "ccds_seq"

    ccdseq_ccds_id: Mapped[str | None] = mapped_column(
        "ccdseq_ccds_id",
        String(50),
        primary_key=True, nullable=False,
        comment="CCDS identifier (primary key)",
    )
    build: Mapped[str | None] = mapped_column(
        "ccdseq_build",
        String(50),
        comment="Genome build version",
    )
    chromosome: Mapped[str | None] = mapped_column(
        "ccdseq_chrom",
        String(50),
        comment="Chromosome",
    )
    sequence: Mapped[str | None] = mapped_column(
        "ccdseq_seq",
        Text,
        comment="Nucleotide sequence",
    )
