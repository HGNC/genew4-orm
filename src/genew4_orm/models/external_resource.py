"""ExternalResource model representing the external_resource table.

This model contains external database/resource information.
"""

from sqlmodel import Field, SQLModel


class ExternalResource(SQLModel, table=True):
    """ExternalResource entity representing the external_resource table.

    External databases and resources linked to gene groups.
    """

    __tablename__ = "external_resource"

    id: int = Field(
        primary_key=True,
        description="Primary key",
    )
    name: str = Field(
        max_length=255,
        nullable=False,
        description="External resource name",
    )
    url: str = Field(
        max_length=255,
        nullable=False,
        description="External resource URL",
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="External resource description",
    )
    approved: bool = Field(
        default=False,
        nullable=False,
        description="Whether resource is approved",
    )

    # Note: Many-to-many with GeneGroup is through FamHasExtResource junction table
    # Query via: session.query(ExternalResource).join(FamHasExtResource).join(GeneGroup)

    def __repr__(self) -> str:
        """Return string representation of ExternalResource."""
        return f"<ExternalResource(id={self.id}, name='{self.name}')>"
