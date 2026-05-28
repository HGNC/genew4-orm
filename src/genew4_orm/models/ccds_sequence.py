"""CcdsSequence model for the ccds_seq table.

Used by hseq-importer (CCDS source sequence lookup).
"""

from sqlalchemy import Column, String, Text
from sqlmodel import Field, SQLModel


class CcdsSequence(SQLModel, table=True):
    """CCDS sequence record.

    Stores the nucleotide sequence associated with a CCDS identifier,
    along with build and chromosome metadata.
    """

    __tablename__ = "ccds_seq"

    ccdseq_ccds_id: str | None = Field(
        default=None,
        primary_key=True,
        max_length=50,
        description="CCDS identifier (primary key)",
    )
    build: str | None = Field(
        default=None,
        sa_column=Column("ccdseq_build", String(50)),
        description="Genome build version",
    )
    chromosome: str | None = Field(
        default=None,
        sa_column=Column("ccdseq_chrom", String(50)),
        description="Chromosome",
    )
    sequence: str | None = Field(
        default=None,
        sa_column=Column("ccdseq_seq", Text),
        description="Nucleotide sequence",
    )
