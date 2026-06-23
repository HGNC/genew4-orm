"""PseudogeneOrg model for the pseudogene_org table.

Used by xref-loader (pseudogene.org loader) for pseudogene cross-references.
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class PseudogeneOrg(DeclarativeBase):
    """Pseudogene.org record.

    Stores pseudogene annotations from pseudogene.org, including
    genomic coordinates, classification, and parent gene linkage.
    """

    __tablename__ = "pseudogene_org"

    porg_id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Pseudogene.org ID (primary key)",
    )
    chromosome: Mapped[str | None] = mapped_column("porg_chr", String(50), comment="Chromosome")
    strand: Mapped[str | None] = mapped_column("porg_strand", String(5), comment="Strand (+/-)")
    start: Mapped[int | None] = mapped_column("porg_start", Integer, comment="Start coordinate")
    end: Mapped[int | None] = mapped_column("porg_end", Integer, comment="End coordinate")
    sequence: Mapped[str | None] = mapped_column("porg_seq", Text, comment="Nucleotide sequence")
    class_: Mapped[str | None] = mapped_column("porg_class", String(255), comment="Pseudogene classification")
    link: Mapped[str | None] = mapped_column("porg_link", String(255), comment="Link to parent gene or resource")
    parent_gene: Mapped[str | None] = mapped_column("porg_parent_gene", String(255), comment="Parent gene identifier")
