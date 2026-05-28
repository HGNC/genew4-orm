"""EnsemblSequence model for the ensembl_seq table.

Used by hseq-importer (Ensembl source sequence lookup) and
coord-builder (Ensembl sub-source).
"""

from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field, SQLModel


class EnsemblSequence(SQLModel, table=True):
    """Ensembl sequence record.

    Stores nucleotide sequences from Ensembl, keyed by Ensembl gene ID,
    with optional transcript-level and source metadata.
    """

    __tablename__ = "ensembl_seq"

    eseq_ensembl_gene_id: str | None = Field(
        default=None,
        primary_key=True,
        max_length=255,
        description="Ensembl gene identifier (ENSG..., primary key)",
    )
    source: str | None = Field(
        default=None,
        sa_column=Column("eseq_source", String(255)),
        description="Data source label",
    )
    defline: str | None = Field(
        default=None,
        sa_column=Column("eseq_defline", Text),
        description="FASTA defline",
    )
    ensembl_transcript_id: str | None = Field(
        default=None,
        sa_column=Column("eseq_ensembl_transcript_id", String(255)),
        description="Ensembl transcript identifier (ENST...)",
    )
    sequence: str | None = Field(
        default=None,
        sa_column=Column("eseq_seq", Text),
        description="Nucleotide sequence",
    )
    length: int | None = Field(
        default=None,
        sa_column=Column("eseq_length", Integer),
        description="Sequence length",
    )
