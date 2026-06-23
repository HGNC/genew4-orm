"""OtterSequence model for the otter_seq table.

Used by hseq-importer (VEGA/Otter source sequence lookup).
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class OtterSequence(DeclarativeBase):
    """VEGA/Otter sequence record.

    Stores nucleotide sequences from the VEGA (Vertebrate Genome Annotation)
    database, keyed by VEGA gene identifier.
    """

    __tablename__ = "otter_seq"

    oseq_gene_id: Mapped[str | None] = mapped_column(
        String(255),
        primary_key=True,
        nullable=False,
        comment="VEGA gene identifier (primary key, join key)",
    )
    defline: Mapped[str | None] = mapped_column("oseq_defline", Text, comment="FASTA defline")
    sequence: Mapped[str | None] = mapped_column("oseq_seq", Text, comment="Nucleotide sequence")
    length: Mapped[int | None] = mapped_column("oseq_length", Integer, comment="Sequence length")
