"""FamHasSpecialist junction model for GeneGroup-Specialist many-to-many relationship."""

from db_common import DeclarativeBase
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column


class FamHasSpecialist(DeclarativeBase):
    """FamHasSpecialist junction entity representing family_has_specialist table.

    This is a junction table for many-to-many relationship between
    GeneGroup (family_new) and Specialist.

    Note: This table uses a composite primary key (specialist_id, gene_group_id)
    and does not have an id column.
    """

    __tablename__ = "family_has_specialist"

    # Foreign keys (these form the composite primary key)
    specialist_id: Mapped[int] = mapped_column(
        "specialist_id",
        Integer,
        ForeignKey("specialist.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to specialist table",
    )
    gene_group_id: Mapped[int] = mapped_column(
        "fam_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to family_new table",
    )

    # Note: Relationships are defined on the main models (Specialist, GeneGroup)
    # using secondary parameter with this table

    def __repr__(self) -> str:
        """Return string representation of FamHasSpecialist."""
        return f"<FamHasSpecialist(specialist_id={self.specialist_id}, gene_group_id={self.gene_group_id})>"
