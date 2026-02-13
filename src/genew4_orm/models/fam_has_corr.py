"""FamHasCorr junction model for GeneGroup-Correspondence many-to-many relationship."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.correspondence import Correspondence
    from genew4_orm.models.gene_group import GeneGroup


class FamHasCorr(SQLModel, table=True):
    """FamHasCorr junction entity representing family_has_correspondence table.

    This is a junction table for many-to-many relationship between
    GeneGroup (family_new) and Correspondence.

    Note: This table uses a composite primary key (corr_id, gene_group_id)
    and does not have an id column.
    """

    __tablename__ = "family_has_correspondence"

    # Foreign keys (these form the composite primary key)
    correspondence_id: int = Field(
        sa_column=Column(
            "corr_id",
            Integer,
            ForeignKey("corr.corr_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to corr table",
    )
    gene_group_id: int = Field(
        sa_column=Column(
            "fam_id",
            Integer,
            ForeignKey("family_new.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to family_new table",
    )

    # Note: Relationships are defined on the main models (Correspondence, GeneGroup)
    # using secondary parameter with this table

    def __repr__(self) -> str:
        """Return string representation of FamHasCorr."""
        return (
            f"<FamHasCorr("
            f"correspondence_id={self.correspondence_id}, gene_group_id={self.gene_group_id})>"
        )
