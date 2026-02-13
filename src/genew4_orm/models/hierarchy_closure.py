"""HierarchyClosure model representing the hierarchy_closure table.

This model contains transitive closure data for hierarchical gene group relationships.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.gene_group import GeneGroup


class HierarchyClosure(SQLModel, table=True):
    """HierarchyClosure entity representing the hierarchy_closure table.

    Transitive closure table for efficient hierarchical queries.
    Each row represents a relationship between an ancestor and descendant
    gene group with the distance (number of levels) between them.
    """

    __tablename__ = "hierarchy_closure"

    # Composite primary key fields
    ancestor_id: int = Field(
        sa_column=Column(
            "parent_fam_id",
            Integer,
            ForeignKey("family_new.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Parent/ancestor gene group ID",
    )
    descendant_id: int = Field(
        sa_column=Column(
            "child_fam_id",
            Integer,
            ForeignKey("family_new.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Child/descendant gene group ID",
    )
    distance: int = Field(
        sa_column=Column(
            "distance",
            Integer,
            primary_key=True,
        ),
        description="Number of levels between ancestor and descendant",
    )

    # Relationships
    ancestor: "GeneGroup" = Relationship(
        back_populates="child_hierarchy_closures",
        sa_relationship_kwargs={
            "primaryjoin": "HierarchyClosure.ancestor_id == GeneGroup.id",
            "foreign_keys": "[HierarchyClosure.ancestor_id]",
        },
    )
    descendant: "GeneGroup" = Relationship(
        back_populates="parent_hierarchy_closures",
        sa_relationship_kwargs={
            "primaryjoin": "HierarchyClosure.descendant_id == GeneGroup.id",
            "foreign_keys": "[HierarchyClosure.descendant_id]",
        },
    )

    def __repr__(self) -> str:
        """Return string representation of HierarchyClosure."""
        return (
            f"<HierarchyClosure(ancestor_id={self.ancestor_id}, "
            f"descendant_id={self.descendant_id}, distance={self.distance})>"
        )
