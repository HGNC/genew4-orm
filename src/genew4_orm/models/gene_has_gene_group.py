"""GeneHasGeneGroup model representing the gene_has_family table.

This is the junction table for the many-to-many relationship
between Gene and GeneGroup, with custom sort order.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.gene import Gene
    from genew4_orm.models.gene_group import GeneGroup


class GeneHasGeneGroup(SQLModel, table=True):
    """GeneHasGeneGroup junction entity representing the gene_has_family table.

    This is the junction table for the many-to-many relationship between
    Gene and GeneGroup. It includes a custom sort_order field.
    """

    __tablename__ = "gene_has_family"

    # Composite primary key: (hgnc_id, family_id)
    # Foreign keys serve as composite primary key
    gene_id: int | None = Field(
        default=None,
        sa_column=Column(
            "hgnc_id",
            ForeignKey("hgnc.hgnc_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to hgnc table (part of composite primary key)",
    )
    gene_group_id: int | None = Field(
        default=None,
        sa_column=Column("family_id", ForeignKey("family_new.id", ondelete="CASCADE"), primary_key=True),
        description="Foreign key to family_new table (part of composite primary key)",
    )

    # Additional fields
    url: str | None = Field(
        default=None,
        sa_column=Column("url", String(255)),
        description="URL for this gene-group association",
    )
    custom_sort: str | None = Field(
        default=None,
        sa_column=Column("custom_sort", String(255)),
        description="Custom sort value for gene within group",
    )

    # Relationships
    gene: "Gene" = Relationship(
        back_populates="gene_has_gene_groups",
        sa_relationship_kwargs={
            "foreign_keys": "[GeneHasGeneGroup.gene_id]",
        },
    )
    gene_group: "GeneGroup" = Relationship(
        back_populates="gene_group_has_genes",
        sa_relationship_kwargs={
            "foreign_keys": "[GeneHasGeneGroup.gene_group_id]",
        },
    )

    def __repr__(self) -> str:
        """Return string representation of GeneHasGeneGroup."""
        return f"<GeneHasGeneGroup(gene_id={self.gene_id}, gene_group_id={self.gene_group_id})>"
