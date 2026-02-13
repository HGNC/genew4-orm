"""GeneGroup model representing the family_new table.

This model contains gene family/group information matching the
TypeScript ORM implementation in hgnc-tools-api.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Text
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from genew4_orm.models.correspondence import Correspondence
    from genew4_orm.models.external_resource import ExternalResource
    from genew4_orm.models.gene_group_alias import GeneGroupAlias
    from genew4_orm.models.gene_has_gene_group import GeneHasGeneGroup
    from genew4_orm.models.hierarchy_closure import HierarchyClosure
    from genew4_orm.models.specialist import Specialist


class GeneGroup(SQLModel, table=True):
    """Gene Group entity representing the family_new table.

    Contains gene family/group information including relationships
    to genes, specialists, external resources, and hierarchical
    parent-child relationships.
    """

    __tablename__ = "family_new"

    # Region: Group
    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key",
    )
    # Note: unique=True removed - database does not enforce this constraint
    name: str = Field(
        max_length=150,
        nullable=False,
        description="Gene group name",
    )
    abbreviation: str | None = Field(
        default=None,
        max_length=50,
        description="Gene group abbreviation",
    )
    editor: str | None = Field(
        default=None,
        max_length=50,
        description="Editor responsible",
    )
    # status field removed - was causing enum type issues

    # type field removed - was causing enum type issues

    pubmed_ids: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="PubMed IDs",
    )
    internal_comments: str | None = Field(
        default=None,
        sa_column=Column("curator_comment", Text),
        description="Internal curator comments",
    )
    public_comments: str | None = Field(
        default=None,
        sa_column=Column("external_note", Text),
        description="Public-facing comments",
    )

    # Region: Description
    label: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("desc_label", String(255)),
        description="Description label",
    )
    source: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("desc_source", String(255)),
        description="Description source",
    )
    typical_gene: str | None = Field(
        default=None,
        max_length=255,
        sa_column=Column("typical_gene", String(255)),
        description="Typical gene for this group",
    )
    description: str | None = Field(
        default=None,
        sa_column=Column("desc_comment", Text),
        description="Full description",
    )

    # Region: Relations
    # One-to-many with GeneHasGeneGroup (cascade delete)
    gene_group_has_genes: list["GeneHasGeneGroup"] = Relationship(
        back_populates="gene_group",
        cascade_delete=True,
    )

    # Many-to-many with Specialist via FamHasSpecialist junction table
    # Query via: session.query(GeneGroup).join(FamHasSpecialist).join(Specialist)

    # One-to-many with GeneGroupAlias
    aliases: list["GeneGroupAlias"] = Relationship(
        back_populates="gene_group",
        cascade_delete=True,
    )

    # Many-to-many with ExternalResource via FamHasExtResource junction table
    # Query via: session.query(GeneGroup).join(FamHasExtResource).join(ExternalResource)

    # Many-to-many with Correspondence via FamHasCorr junction table
    # Query via: session.query(GeneGroup).join(FamHasCorr).join(Correspondence)

    # TODO: Self-referential many-to-many for hierarchy - requires junction table
    # # Self-referential many-to-many for hierarchy (parents)
    # parents: list["GeneGroup"] = Relationship(
    #     back_populates="children",
    #     sa_relationship_kwargs={
    #         "secondary": "hierarchy",
    #         "primaryjoin": "GeneGroup.id == hierarchy.c.child_fam_id",
    #         "secondaryjoin": "GeneGroup.id == hierarchy.c.parent_fam_id",
    #         "foreign_keys": "[hierarchy.c.child_fam_id, hierarchy.c.parent_fam_id]",
    #     },
    # )
    #
    # # Self-referential many-to-many for hierarchy (children) - inverse of parents
    # children: list["GeneGroup"] = Relationship(
    #     back_populates="parents",
    # )

    # One-to-many with HierarchyClosure as parent
    parent_hierarchy_closures: list["HierarchyClosure"] = Relationship(
        back_populates="ancestor",
        sa_relationship_kwargs={
            "primaryjoin": "GeneGroup.id == HierarchyClosure.ancestor_id",
            "foreign_keys": "[HierarchyClosure.ancestor_id]",
        },
    )

    # One-to-many with HierarchyClosure as child
    child_hierarchy_closures: list["HierarchyClosure"] = Relationship(
        back_populates="descendant",
        sa_relationship_kwargs={
            "primaryjoin": "GeneGroup.id == HierarchyClosure.descendant_id",
            "foreign_keys": "[HierarchyClosure.descendant_id]",
        },
    )

    def __repr__(self) -> str:
        """Return string representation of GeneGroup."""
        return f"<GeneGroup(id={self.id}, name='{self.name}')>"
