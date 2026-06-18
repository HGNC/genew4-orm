"""Specialist model representing the specialist table.

This model contains specialist organization information.
"""

from db_common import DeclarativeBase
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Specialist(DeclarativeBase):
    """Specialist entity representing the specialist table.

    External specialist organizations that collaborate with HGNC.
    """

    __tablename__ = "specialist"

    id: Mapped[int | None] = mapped_column(
        Integer,
        primary_key=True, nullable=False,
        comment="Primary key",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Specialist organization name")
    address: Mapped[str] = mapped_column(Text, nullable=False, comment="Specialist organization address")
    url: Mapped[str | None] = mapped_column(String(255), comment="Specialist organization website URL")

    # Note: Many-to-many with GeneGroup is through FamHasSpecialist junction table
    # Query via: session.query(Specialist).join(FamHasSpecialist).join(GeneGroup)

    def __repr__(self) -> str:
        """Return string representation of Specialist."""
        return f"<Specialist(id={self.id}, name='{self.name}')>"
