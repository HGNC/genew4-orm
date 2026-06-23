"""FamHasCorr junction model for GeneGroup-Correspondence many-to-many relationship."""

from db_common import DeclarativeBase
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column


class FamHasCorr(DeclarativeBase):
    """FamHasCorr junction entity representing family_has_correspondence table.

    This is a junction table for many-to-many relationship between
    GeneGroup (family_new) and Correspondence.

    Note: This table uses a composite primary key (corr_id, gene_group_id)
    and does not have an id column.
    """

    __tablename__ = "family_has_correspondence"

    # Foreign keys (these form the composite primary key)
    correspondence_id: Mapped[int] = mapped_column(
        "corr_id",
        Integer,
        ForeignKey("corr.corr_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="Foreign key to corr table",
    )
    gene_group_id: Mapped[int] = mapped_column(
        "fam_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="Foreign key to family_new table",
    )

    # Note: Relationships are defined on the main models (Correspondence, GeneGroup)
    # using secondary parameter with this table

    def __repr__(self) -> str:
        """Return string representation of FamHasCorr."""
        return f"<FamHasCorr(correspondence_id={self.correspondence_id}, gene_group_id={self.gene_group_id})>"
