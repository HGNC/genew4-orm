"""GeneGroupAlias model representing the family_alias table.

This model contains alternative names for gene groups.
"""

from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.gene_group import GeneGroup


class GeneGroupAlias(DeclarativeBase):
    """GeneGroupAlias entity representing the family_alias table.

    Alternative names for gene groups with cascade delete.
    """

    __tablename__ = "family_alias"

    id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="Primary key",
    )
    alias: Mapped[str] = mapped_column(String(255), nullable=False, comment="Alternative name for the gene group")

    # Foreign key to GeneGroup
    gene_group_id: Mapped[int | None] = mapped_column(
        "family_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        comment="Foreign key to family_new (gene group) table",
    )
    gene_group: Mapped["GeneGroup"] = relationship(
        back_populates="aliases",
        foreign_keys="[GeneGroupAlias.gene_group_id]",
    )

    def __repr__(self) -> str:
        """Return string representation of GeneGroupAlias."""
        return f"<GeneGroupAlias(id={self.id}, alias='{self.alias}')>"
