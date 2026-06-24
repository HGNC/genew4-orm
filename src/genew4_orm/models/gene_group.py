"""GeneGroup model representing the family_new table.

This model contains gene family/group information matching the
TypeScript ORM implementation in hgnc-tools-api.
"""

from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from genew4_orm.enums import GeneGroupStatus, GeneGroupType, enum_field

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
        primary_key=True,
        nullable=False,
        comment="Primary key",
    )
    # Note: unique=True removed - database does not enforce this constraint
    name: Mapped[str] = mapped_column(String(150), nullable=False, comment="Gene group name")
    abbreviation: Mapped[str | None] = mapped_column(String(50), comment="Gene group abbreviation")
    editor: Mapped[str | None] = mapped_column(String(50), comment="Editor responsible")

    # status / type are real family_new columns backed by PostgreSQL enum types,
    # mirroring the TypeScript ORM (hgnc-tools-api GeneGroup entity).
    # native_enum=False sends the value as text (no auto-created PG enum type),
    # which the real enum column accepts; create_constraint adds a CHECK on
    # create_all()-built (e.g. SQLite) test schemas. Same pattern as Comment.status.
    status: Mapped[str] = enum_field(
        GeneGroupStatus,
        default=GeneGroupStatus.INTERNAL,
        nullable=False,
        column_name="status",
    )
    type: Mapped[str | None] = enum_field(
        GeneGroupType,
        default=GeneGroupType.SET,
        nullable=True,
        column_name="type",
    )

    pubmed_ids: Mapped[str | None] = mapped_column(Text, comment="PubMed IDs")
    internal_comments: Mapped[str | None] = mapped_column("curator_comment", Text, comment="Internal curator comments")
    public_comments: Mapped[str | None] = mapped_column("external_note", Text, comment="Public-facing comments")

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

    def __init__(self, **kwargs: object) -> None:
        """Initialize a GeneGroup, applying SQLModel-parity instantiation defaults.

        Plain SQLAlchemy 2.0 only applies ``mapped_column(default=...)`` at flush,
        not construction. ``status`` (NOT NULL) and ``type`` get their defaults at
        instantiation (as the TypeScript ORM did), unless explicitly provided.
        """
        if "status" not in kwargs:
            self.status = GeneGroupStatus.INTERNAL
        if "type" not in kwargs:
            self.type = GeneGroupType.SET
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """Return string representation of GeneGroup."""
        return f"<GeneGroup(id={self.id}, name='{self.name}')>"
