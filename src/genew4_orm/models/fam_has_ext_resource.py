"""FamHasExtResource junction model for GeneGroup-ExternalResource many-to-many relationship.

This is a junction table for the many-to-many relationship between
GeneGroup (family_new) and ExternalResource.
Note: This table uses (family_id, ext_id) as composite primary key.
"""

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, SQLModel


class FamHasExtResource(SQLModel, table=True):
    """FamHasExtResource junction entity representing the family_has_external_resource table.

    This is the junction table for the many-to-many relationship between
    GeneGroup (family_new) and ExternalResource.
    Uses (family_id, ext_id) as composite primary key.
    """

    __tablename__ = "family_has_external_resource"

    # Composite primary key (no separate id column)
    external_resource_id: int = Field(
        sa_column=Column(
            "ext_id",
            Integer,
            ForeignKey("external_resource.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to external_resource table",
    )
    gene_group_id: int = Field(
        sa_column=Column(
            "family_id",
            Integer,
            ForeignKey("family_new.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Foreign key to family_new table",
    )

    # Note: Relationships are defined on the main models (ExternalResource, GeneGroup)
    # using the secondary parameter with this table

    def __repr__(self) -> str:
        """Return string representation of FamHasExtResource."""
        return (
            f"<FamHasExtResource("
            f"external_resource_id={self.external_resource_id}, "
            f"gene_group_id={self.gene_group_id})>"
        )
