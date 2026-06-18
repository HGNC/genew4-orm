"""FamHasExtResource junction model for GeneGroup-ExternalResource many-to-many relationship.

This is a junction table for the many-to-many relationship between
GeneGroup (family_new) and ExternalResource.
Note: This table uses (family_id, ext_id) as composite primary key.
"""

from db_common import DeclarativeBase
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column


class FamHasExtResource(DeclarativeBase):
    """FamHasExtResource junction entity representing the family_has_external_resource table.

    This is the junction table for the many-to-many relationship between
    GeneGroup (family_new) and ExternalResource.
    Uses (family_id, ext_id) as composite primary key.
    """

    __tablename__ = "family_has_external_resource"

    # Composite primary key (no separate id column)
    external_resource_id: Mapped[int] = mapped_column(
        "ext_id",
        Integer,
        ForeignKey("external_resource.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to external_resource table",
    )
    gene_group_id: Mapped[int] = mapped_column(
        "family_id",
        Integer,
        ForeignKey("family_new.id", ondelete="CASCADE"),
        primary_key=True, nullable=False,
        comment="Foreign key to family_new table",
    )

    # Note: Relationships are defined on the main models (ExternalResource, GeneGroup)
    # using the secondary parameter with this table

    def __repr__(self) -> str:
        """Return string representation of FamHasExtResource."""
        return (
            f"<FamHasExtResource(external_resource_id={self.external_resource_id}, gene_group_id={self.gene_group_id})>"
        )
