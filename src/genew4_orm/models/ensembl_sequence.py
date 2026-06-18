"""EnsemblSequence model for the ensembl_seq table.

Used by hseq-importer (Ensembl source sequence lookup) and
coord-builder (Ensembl sub-source).
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class EnsemblSequence(DeclarativeBase):
    """Ensembl sequence record.

    Stores nucleotide sequences from Ensembl, keyed by Ensembl gene ID,
    with optional transcript-level and source metadata.
    """

    __tablename__ = "ensembl_seq"

    eseq_ensembl_gene_id: Mapped[str | None] = mapped_column(
        String(255),
        primary_key=True, nullable=False,
        comment="Ensembl gene identifier (ENSG..., primary key)",
    )
    source: Mapped[str | None] = mapped_column(
        "eseq_source", String(255), comment="Data source label"
    )
    defline: Mapped[str | None] = mapped_column("eseq_defline", Text, comment="FASTA defline")
    ensembl_transcript_id: Mapped[str | None] = mapped_column(
        "eseq_ensembl_transcript_id", String(255), comment="Ensembl transcript identifier (ENST...)"
    )
    sequence: Mapped[str | None] = mapped_column("eseq_seq", Text, comment="Nucleotide sequence")
    length: Mapped[int | None] = mapped_column("eseq_length", Integer, comment="Sequence length")
