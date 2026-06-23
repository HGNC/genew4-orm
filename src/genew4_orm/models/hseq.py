"""Hseq model for the hseq table.

Used by hseq-importer for inserts and post-load lookup of
canonical sequence records.
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Hseq(DeclarativeBase):
    """HGNC sequence record.

    Stores curated sequence entries with metadata including source,
    editor, molecule type, priority, and defline-parsed HGNC references.
    """

    __tablename__ = "hseq"

    hseq_id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Auto-incrementing primary key",
    )
    ext: Mapped[str | None] = mapped_column("hseq_ext", String(50), comment="External source identifier")
    editor: Mapped[str | None] = mapped_column("hseq_editor", String(50), comment="Editor who submitted the record")
    molecule: Mapped[str | None] = mapped_column("hseq_molecule", String(20), comment="Molecule type (DNA, RNA, etc.)")
    submitted: Mapped[int | None] = mapped_column("hseq_submitted", Integer, comment="Submission flag")
    status: Mapped[str | None] = mapped_column("hseq_status", String(50), comment="Record status")
    priority: Mapped[int | None] = mapped_column("hseq_priority", Integer, comment="Priority ranking")
    run_notes: Mapped[str | None] = mapped_column("hseq_run_notes", Text, comment="Notes from the import run")
    comment: Mapped[str | None] = mapped_column("hseq_comment", Text, comment="Comment on the sequence")
    entry_class: Mapped[str | None] = mapped_column("hseq_entry_class", String(50), comment="Entry classification")
    is_new: Mapped[str | None] = mapped_column("hseq_isnew", String(10), comment="New entry flag")
    defline: Mapped[str | None] = mapped_column(
        "hseq_defline", Text, comment="FASTA defline containing HGNC ID and metadata"
    )
    sequence: Mapped[str | None] = mapped_column("hseq_seq", Text, comment="Nucleotide sequence")
