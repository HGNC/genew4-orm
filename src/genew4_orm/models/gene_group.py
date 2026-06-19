"""GeneGroup model representing the family_new table.

This model contains gene family/group information matching the
TypeScript ORM implementation in hgnc-tools-api.
"""

from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.gene_group_alias import GeneGroupAlias
    from genew4_orm.models.gene_has_gene_group import GeneHasGeneGroup
    from genew4_orm.models.hierarchy_closure import HierarchyClosure


class GeneGroup(DeclarativeBase):
    """Gene Group entity representing the family_new table.

    Contains gene family/group information including relationships
    to genes, specialists, external resources, and hierarchical
    parent-child relationships.
    """

    __tablename__ = "family_new"

    # Region: Group
    id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True, nullable=False,
        comment="Primary key",
    )
    # Note: unique=True removed - database does not enforce this constraint
    name: Mapped[str] = mapped_column(String(150), nullable=False, comment="Gene group name")
    abbreviation: Mapped[str | None] = mapped_column(String(50), comment="Gene group abbreviation")
    editor: Mapped[str | None] = mapped_column(String(50), comment="Editor responsible")
    # status field removed - was causing enum type issues

    # type field removed - was causing enum type issues

    pubmed_ids: Mapped[str | None] = mapped_column(Text, comment="PubMed IDs")
    internal_comments: Mapped[str | None] = mapped_column(
        "curator_comment", Text, comment="Internal curator comments"
    )
    public_comments: Mapped[str | None] = mapped_column(
        "external_note", Text, comment="Public-facing comments"
    )

    # Region: Description
    label: Mapped[str | None] = mapped_column("desc_label", String(255), comment="Description label")
    source: Mapped[str | None] = mapped_column("desc_source", String(255), comment="Description source")
    typical_gene: Mapped[str | None] = mapped_column(String(255), comment="Typical gene for this group")
    description: Mapped[str | None] = mapped_column("desc_comment", Text, comment="Full description")

    # Region: Relations
    # One-to-many with GeneHasGeneGroup (cascade delete)
    gene_group_has_genes: Mapped[list["GeneHasGeneGroup"]] = relationship(
        back_populates="gene_group",
        cascade="all, delete-orphan",
    )

    # Many-to-many with Specialist via FamHasSpecialist junction table
    # Query via: session.scalars(select(GeneGroup).join(FamHasSpecialist).join(Specialist)).all()

    # One-to-many with GeneGroupAlias
    aliases: Mapped[list["GeneGroupAlias"]] = relationship(
        back_populates="gene_group",
        cascade="all, delete-orphan",
    )

    # Many-to-many with ExternalResource via FamHasExtResource junction table
    # Query via: session.scalars(select(GeneGroup).join(FamHasExtResource).join(ExternalResource)).all()

    # Many-to-many with Correspondence via FamHasCorr junction table
    # Query via: session.scalars(select(GeneGroup).join(FamHasCorr).join(Correspondence)).all()

    # TODO: Self-referential many-to-many for hierarchy - requires junction table
    # # Self-referential many-to-many for hierarchy (parents)
    # parents: list["GeneGroup"] = relationship(
    #     back_populates="children",
    #     secondary="hierarchy",
    #     primaryjoin="GeneGroup.id == hierarchy.c.child_fam_id",
    #     secondaryjoin="GeneGroup.id == hierarchy.c.parent_fam_id",
    #     foreign_keys="[hierarchy.c.child_fam_id, hierarchy.c.parent_fam_id]",
    # )
    #
    # # Self-referential many-to-many for hierarchy (children) - inverse of parents
    # children: list["GeneGroup"] = relationship(
    #     back_populates="parents",
    # )

    # One-to-many with HierarchyClosure as parent
    parent_hierarchy_closures: Mapped[list["HierarchyClosure"]] = relationship(
        back_populates="ancestor",
        primaryjoin="GeneGroup.id == HierarchyClosure.ancestor_id",
        foreign_keys="[HierarchyClosure.ancestor_id]",
    )

    # One-to-many with HierarchyClosure as child
    child_hierarchy_closures: Mapped[list["HierarchyClosure"]] = relationship(
        back_populates="descendant",
        primaryjoin="GeneGroup.id == HierarchyClosure.descendant_id",
        foreign_keys="[HierarchyClosure.descendant_id]",
    )

    def __repr__(self) -> str:
        """Return string representation of GeneGroup."""
        return f"<GeneGroup(id={self.id}, name='{self.name}')>"
