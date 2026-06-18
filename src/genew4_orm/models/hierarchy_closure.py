"""HierarchyClosure model representing the hierarchy_closure table.

This model contains transitive closure data for hierarchical gene group relationships.
"""

from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.gene_group import GeneGroup


class HierarchyClosure(DeclarativeBase):
    """HierarchyClosure entity representing the hierarchy_closure table.

    Transitive closure table for efficient hierarchical queries.
    Each row represents a relationship between an ancestor and descendant
    gene group with the distance (number of levels) between them.
    """

    __tablename__ = "hierarchy_closure"

    # Composite primary key fields
    ancestor_id: Mapped[int] = mapped_column(
        "parent_fam_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Parent/ancestor gene group ID",
    )
    descendant_id: Mapped[int] = mapped_column(
        "child_fam_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Child/descendant gene group ID",
    )
    distance: Mapped[int] = mapped_column(
        "distance",
        Integer,
        primary_key=True, nullable=False,
        comment="Number of levels between ancestor and descendant",
    )

    # Relationships
    ancestor: Mapped["GeneGroup"] = relationship(
        back_populates="child_hierarchy_closures",
        primaryjoin="HierarchyClosure.ancestor_id == GeneGroup.id",
        foreign_keys="[HierarchyClosure.ancestor_id]",
    )
    descendant: Mapped["GeneGroup"] = relationship(
        back_populates="parent_hierarchy_closures",
        primaryjoin="HierarchyClosure.descendant_id == GeneGroup.id",
        foreign_keys="[HierarchyClosure.descendant_id]",
    )

    def __repr__(self) -> str:
        """Return string representation of HierarchyClosure."""
        return (
            f"<HierarchyClosure(ancestor_id={self.ancestor_id}, "
            f"descendant_id={self.descendant_id}, distance={self.distance})>"
        )
