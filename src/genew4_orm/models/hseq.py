"""Hseq model for the hseq table.

Used by hseq-importer for inserts and post-load lookup of
canonical sequence records.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field, SQLModel


class Hseq(SQLModel, table=True):
    """HGNC sequence record.

    Stores curated sequence entries with metadata including source,
    editor, molecule type, priority, and defline-parsed HGNC references.
    """

    __tablename__ = "hseq"

    hseq_id: int | None = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key",
    )
    ext: str | None = Field(
        default=None,
        sa_column=Column("hseq_ext", String(50)),
        description="External source identifier",
    )
    editor: str | None = Field(
        default=None,
        sa_column=Column("hseq_editor", String(50)),
        description="Editor who submitted the record",
    )
    molecule: str | None = Field(
        default=None,
        sa_column=Column("hseq_molecule", String(20)),
        description="Molecule type (DNA, RNA, etc.)",
    )
    submitted: int | None = Field(
        default=None,
        sa_column=Column("hseq_submitted", Integer),
        description="Submission flag",
    )
    status: str | None = Field(
        default=None,
        sa_column=Column("hseq_status", String(50)),
        description="Record status",
    )
    priority: int | None = Field(
        default=None,
        sa_column=Column("hseq_priority", Integer),
        description="Priority ranking",
    )
    run_notes: str | None = Field(
        default=None,
        sa_column=Column("hseq_run_notes", Text),
        description="Notes from the import run",
    )
    comment: str | None = Field(
        default=None,
        sa_column=Column("hseq_comment", Text),
        description="Comment on the sequence",
    )
    entry_class: str | None = Field(
        default=None,
        sa_column=Column("hseq_entry_class", String(50)),
        description="Entry classification",
    )
    is_new: str | None = Field(
        default=None,
        sa_column=Column("hseq_isnew", String(10)),
        description="New entry flag",
    )
    defline: str | None = Field(
        default=None,
        sa_column=Column("hseq_defline", Text),
        description="FASTA defline containing HGNC ID and metadata",
    )
    sequence: str | None = Field(
        default=None,
        sa_column=Column("hseq_seq", Text),
        description="Nucleotide sequence",
    )
