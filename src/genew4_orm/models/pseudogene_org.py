"""PseudogeneOrg model for the pseudogene_org table.

Used by xref-loader (pseudogene.org loader) for pseudogene cross-references.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field, SQLModel


class PseudogeneOrg(SQLModel, table=True):
    """Pseudogene.org record.

    Stores pseudogene annotations from pseudogene.org, including
    genomic coordinates, classification, and parent gene linkage.
    """

    __tablename__ = "pseudogene_org"

    porg_id: int | None = Field(
        default=None,
        primary_key=True,
        description="Pseudogene.org ID (primary key)",
    )
    chromosome: str | None = Field(
        default=None,
        sa_column=Column("porg_chr", String(50)),
        description="Chromosome",
    )
    strand: str | None = Field(
        default=None,
        sa_column=Column("porg_strand", String(5)),
        description="Strand (+/-)",
    )
    start: int | None = Field(
        default=None,
        sa_column=Column("porg_start", Integer),
        description="Start coordinate",
    )
    end: int | None = Field(
        default=None,
        sa_column=Column("porg_end", Integer),
        description="End coordinate",
    )
    sequence: str | None = Field(
        default=None,
        sa_column=Column("porg_seq", Text),
        description="Nucleotide sequence",
    )
    class_: str | None = Field(
        default=None,
        sa_column=Column("porg_class", String(255)),
        description="Pseudogene classification",
    )
    link: str | None = Field(
        default=None,
        sa_column=Column("porg_link", String(255)),
        description="Link to parent gene or resource",
    )
    parent_gene: str | None = Field(
        default=None,
        sa_column=Column("porg_parent_gene", String(255)),
        description="Parent gene identifier",
    )
