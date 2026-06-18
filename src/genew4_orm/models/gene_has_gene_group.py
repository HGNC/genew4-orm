"""GeneHasGeneGroup model representing the gene_has_family table.

This is the junction table for the many-to-many relationship
between Gene and GeneGroup, with custom sort order.
"""

from typing import TYPE_CHECKING

from db_common import DeclarativeBase
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from genew4_orm.models.gene import Gene
    from genew4_orm.models.gene_group import GeneGroup


class GeneHasGeneGroup(DeclarativeBase):
    """GeneHasGeneGroup junction entity representing the gene_has_family table.

    This is the junction table for the many-to-many relationship between
    Gene and GeneGroup. It includes a custom sort_order field.
    """

    __tablename__ = "gene_has_family"

    # Composite primary key: (hgnc_id, family_id)
    # Foreign keys serve as composite primary key
    gene_id: Mapped[int | None] = mapped_column(
        "hgnc_id",
        Integer,
        ForeignKey("hgnc.hgnc_id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to hgnc table (part of composite primary key)",
    )
    gene_group_id: Mapped[int | None] = mapped_column(
        "family_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to family_new table (part of composite primary key)",
    )

    # Additional fields
    url: Mapped[str | None] = mapped_column("url", String(255), comment="URL for this gene-group association")
    custom_sort: Mapped[str | None] = mapped_column(
        "custom_sort", String(255), comment="Custom sort value for gene within group"
    )

    # Relationships
    gene: Mapped["Gene"] = relationship(
        back_populates="gene_has_gene_groups",
        foreign_keys="[GeneHasGeneGroup.gene_id]",
    )
    gene_group: Mapped["GeneGroup"] = relationship(
        back_populates="gene_group_has_genes",
        foreign_keys="[GeneHasGeneGroup.gene_group_id]",
    )

    def __repr__(self) -> str:
        """Return string representation of GeneHasGeneGroup."""
        return f"<GeneHasGeneGroup(gene_id={self.gene_id}, gene_group_id={self.gene_group_id})>"
