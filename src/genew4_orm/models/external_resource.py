"""ExternalResource model representing the external_resource table.

This model contains external database/resource information.
"""

from db_common import DeclarativeBase
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ExternalResource(DeclarativeBase):
    """ExternalResource entity representing the external_resource table.

    External databases and resources linked to gene groups.
    """

    __tablename__ = "external_resource"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True, nullable=False,
        comment="Primary key",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="External resource name")
    url: Mapped[str] = mapped_column(String(255), nullable=False, comment="External resource URL")
    description: Mapped[str | None] = mapped_column(
        String(255), comment="External resource description"
    )
    approved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether resource is approved"
    )

    # Note: Many-to-many with GeneGroup is through FamHasExtResource junction table
    # Query via: session.query(ExternalResource).join(FamHasExtResource).join(GeneGroup)

    def __repr__(self) -> str:
        """Return string representation of ExternalResource."""
        return f"<ExternalResource(id={self.id}, name='{self.name}')>"
