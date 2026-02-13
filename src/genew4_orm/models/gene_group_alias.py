"""GeneGroupAlias model representing the family_alias table.

This model contains alternative names for gene groups.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.gene_group import GeneGroup


class GeneGroupAlias(SQLModel, table=True):
    """GeneGroupAlias entity representing the family_alias table.

    Alternative names for gene groups with cascade delete.
    """

    __tablename__ = "family_alias"

    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Primary key",
    )
    alias: str = Field(
        max_length=255,
        nullable=False,
        description="Alternative name for the gene group",
    )

    # Foreign key to GeneGroup
    gene_group_id: int | None = Field(
        default=None,
        sa_column=Column(
            "family_id",
            Integer,
            ForeignKey("family_new.id", ondelete="CASCADE"),
        ),
        description="Foreign key to family_new (gene group) table",
    )
    gene_group: "GeneGroup" = Relationship(
        back_populates="aliases",
        sa_relationship_kwargs={
            "foreign_keys": "[GeneGroupAlias.gene_group_id]",
        },
    )

    def __repr__(self) -> str:
        """Return string representation of GeneGroupAlias."""
        return f"<GeneGroupAlias(id={self.id}, alias='{self.alias}')>"
