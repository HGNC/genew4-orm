"""FamHasSpecialist junction model for GeneGroup-Specialist many-to-many relationship."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from genew4_orm.models.gene_group import GeneGroup
    from genew4_orm.models.specialist import Specialist


class FamHasSpecialist(SQLModel, table=True):
    """FamHasSpecialist junction entity representing family_has_specialist table.

    This is a junction table for many-to-many relationship between
    GeneGroup (family_new) and Specialist.

    Note: This table uses a composite primary key (specialist_id, gene_group_id)
    and does not have an id column.
    """

    __tablename__ = "family_has_specialist"

    # Foreign keys (these form the composite primary key)
    specialist_id: int = Field(
        sa_column=Column(
            "specialist_id",
            Integer,
            ForeignKey("specialist.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to specialist table",
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

    # Note: Relationships are defined on the main models (Specialist, GeneGroup)
    # using secondary parameter with this table

    def __repr__(self) -> str:
        """Return string representation of FamHasSpecialist."""
        return (
            f"<FamHasSpecialist("
            f"specialist_id={self.specialist_id}, gene_group_id={self.gene_group_id})>"
        )
