"""OtterSequence model for the otter_seq table.

Used by hseq-importer (VEGA/Otter source sequence lookup).
"""

from sqlalchemy import Column, Integer, Text
from sqlmodel import Field, SQLModel


class OtterSequence(SQLModel, table=True):
    """VEGA/Otter sequence record.

    Stores nucleotide sequences from the VEGA (Vertebrate Genome Annotation)
    database, keyed by VEGA gene identifier.
    """

    __tablename__ = "otter_seq"

    oseq_gene_id: str | None = Field(
        default=None,
        primary_key=True,
        max_length=255,
        description="VEGA gene identifier (primary key, join key)",
    )
    defline: str | None = Field(
        default=None,
        sa_column=Column("oseq_defline", Text),
        description="FASTA defline",
    )
    sequence: str | None = Field(
        default=None,
        sa_column=Column("oseq_seq", Text),
        description="Nucleotide sequence",
    )
    length: int | None = Field(
        default=None,
        sa_column=Column("oseq_length", Integer),
        description="Sequence length",
    )
